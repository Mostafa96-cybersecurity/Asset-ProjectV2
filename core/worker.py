# -*- coding: utf-8 -*-
import ipaddress
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt6.QtCore import QThread, pyqtSignal

# ← الاستيرادات الصحيحة حسب هيكل مشروعك الحالي
from core.smart_collector import SmartDeviceCollector
# from export.excel_exporter import (  # Disabled - Database-only system
#     open_assets_workbook, ensure_assets_sheet, ensure_errors_sheet,
#     upsert_into_assets, append_error_row,
#     autosize_and_wrap, find_row_by_ip, ASSET_HEADERS, excel_sanitize,
#     save_workbook
# )
from utils.helpers import which
# from core.excel_db_sync import get_sync_manager  # Disabled - Database-only system

NMAP_BIN = which("nmap")


def _safe_log(log_sink, msg: str):
    try:
        if hasattr(log_sink, "emit"):
            log_sink.emit(msg)
            return
    except Exception:
        pass
    try:
        log_sink(msg)
    except Exception:
        print(msg)


class ADWorker(QThread):
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal(bool)

    def __init__(self, server, base_dn, user, pwd, use_ssl, excel_file, parent=None):
        super().__init__(parent)
        self.server = server
        self.base_dn = base_dn
        self.user = user
        self.pwd = pwd
        self.use_ssl = use_ssl
        self.excel_file = excel_file

    def run(self):
        # AD functionality temporarily disabled during project cleanup
        _safe_log(self.log_message, "AD functionality currently disabled")
        self.finished_ok.emit(False)
        return
        
        # try:
        #     from ad_fetcher.ad_fetcher import ad_fetch_computers, merge_ad_into_assets
        # except Exception as e:
        #     _safe_log(self.log_message, f"AD import error: {e}")
        #     self.finished_ok.emit(False)
        #     return

        try:
            _safe_log(self.log_message, "Fetching computers from AD...")
            res = ad_fetch_computers(self.server, self.base_dn, self.user, self.pwd, use_ssl=self.use_ssl)
            if isinstance(res, dict) and "Error" in res:
                _safe_log(self.log_message, res["Error"])
                self.finished_ok.emit(False)
                return
            _safe_log(self.log_message, f"AD fetched {len(res)} computer objects. Merging...")
            merge_ad_into_assets(res, self.excel_file, self.log_message)
            self.finished_ok.emit(True)
        except Exception as e:
            _safe_log(self.log_message, f"AD worker error: {e}")
            self.finished_ok.emit(False)


class DeviceInfoCollector(QThread):
    update_progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished_with_status = pyqtSignal(bool)

    def __init__(self, targets, win_creds, linux_creds, snmp_v2c, snmp_v3, excel_file, use_http=True, parent=None):
        super().__init__(parent)
        self.targets = targets
        self.win_creds = win_creds or []
        self.linux_creds = linux_creds or []
        self.snmp_v2c = snmp_v2c or []
        self.snmp_v3 = snmp_v3 or {}
        self.excel_file = excel_file
        self.use_http = use_http
        self._cancel_event = threading.Event()

    def stop(self):
        self._cancel_event.set()

    def _expand_targets(self) -> list[str]:
        ips = []
        for t in self.targets:
            t = t.strip()
            if not t:
                continue
            try:
                if "/" in t:
                    net = ipaddress.ip_network(t, strict=False)
                    if net.num_addresses > 1:
                        ips.extend([str(h) for h in net.hosts()])
                    else:
                        ips.append(str(net.network_address))
                else:
                    ips.append(str(ipaddress.ip_address(t)))
            except Exception:
                _safe_log(self.log_message, f"Invalid target skipped: {t}")
        uniq, seen = [], set()
        for ip in ips:
            if ip not in seen:
                seen.add(ip)
                uniq.append(ip)
        return uniq

    def run(self):
        canceled = False
        try:
            ip_list = self._expand_targets()
            if not ip_list:
                _safe_log(self.log_message, "No valid targets to scan.")
                self.update_progress.emit(0)
                self.finished_with_status.emit(False)
                return

            _safe_log(self.log_message, f"Starting smart collection for {len(ip_list)} targets...")

            # Step 1: Smart ping scan for alive devices only
            smart_collector = SmartDeviceCollector()
            alive_devices = smart_collector.scan_alive_devices(ip_list)
            
            if not alive_devices:
                _safe_log(self.log_message, "No alive devices found.")
                self.update_progress.emit(100)
                self.finished_with_status.emit(False)
                return

            _safe_log(self.log_message, f"Found {len(alive_devices)} alive devices. Starting data collection...")

            # Step 2: Process only alive devices with smart OS detection
            max_workers = min(10, len(alive_devices))
            lock = threading.Lock()
            completed = 0
            successful = 0

            def process_alive_device(ip_str: str):
                nonlocal completed, successful
                
                if self._cancel_event.is_set():
                    return
                
                try:
                    # Step 2a: Detect OS type
                    device_type = smart_collector.detect_os_type(ip_str)
                    
                    if device_type == "Unknown":
                        _safe_log(self.log_message, f"⚠️ Skipping {ip_str} - unknown device type")
                        return
                    
                    _safe_log(self.log_message, f"🔍 {ip_str} detected as {device_type}")
                    
                    # Step 2b: Prepare credentials
                    credentials = {
                        'windows': {},
                        'linux': {}
                    }
                    
                    # Add Windows credentials
                    for cred in self.win_creds:
                        if cred.get('username'):
                            credentials['windows'] = {
                                'username': cred.get('username'),
                                'password': cred.get('password', '')
                            }
                            break
                    
                    # Add Linux credentials  
                    for cred in self.linux_creds:
                        if cred.get('username'):
                            credentials['linux'] = {
                                'username': cred.get('username'),
                                'password': cred.get('password', '')
                            }
                            break
                    
                    # Step 2c: Collect device data
                    device_data = smart_collector.collect_device_data(ip_str, device_type, credentials)
                    
                    if device_data:
                        # Step 2d: Save to appropriate sheet with auto-sync
                        if smart_collector.save_to_appropriate_sheet(device_data, device_type, self.excel_file):
                            with lock:
                                successful += 1
                            _safe_log(self.log_message, f"✅ {ip_str} ({device_type}) data collected and saved")
                        else:
                            _safe_log(self.log_message, f"⚠️ {ip_str} data collected but save failed")
                    else:
                        _safe_log(self.log_message, f"❌ {ip_str} data collection failed")
                        
                except Exception as e:
                    _safe_log(self.log_message, f"❌ Error processing {ip_str}: {e}")
                
                finally:
                    with lock:
                        completed += 1
                        progress = int((completed / len(alive_devices)) * 100)
                        self.update_progress.emit(progress)

            # Process all alive devices
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(process_alive_device, ip): ip for ip in alive_devices}
                
                for future in as_completed(futures):
                    if self._cancel_event.is_set():
                        canceled = True
                        break

            if not canceled:
                _safe_log(self.log_message, f"🎉 Collection completed! {successful}/{len(alive_devices)} devices processed successfully.")
                _safe_log(self.log_message, "📊 Check the Excel file for results in:")
                _safe_log(self.log_message, "   • Windows Devices (workstations)")
                _safe_log(self.log_message, "   • Windows Server (servers)")
                _safe_log(self.log_message, "   • Linux Devices (Linux/Unix systems)")
                
                self.update_progress.emit(100)
                self.finished_with_status.emit(True)
            else:
                _safe_log(self.log_message, "⏹️ Collection was canceled by user")
                self.finished_with_status.emit(False)

        except Exception as e:
            _safe_log(self.log_message, f"💥 Fatal error during collection: {e}")
            self.finished_with_status.emit(False)
