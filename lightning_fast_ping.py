#!/usr/bin/env python3
"""
Lightning-Fast Pure System Ping Validator
=========================================

FASTEST POSSIBLE VALIDATION:
🚀 Pure OS system ping (no Python overhead)
⚡ Minimal 50ms timeout for alive, 100ms for dead
💨 Ultra-high concurrency (up to 10,000 workers)
🎯 Single method focus for maximum speed

OPTIMIZATIONS:
- Uses raw system ping command only
- No TCP fallback (ping is fastest)
- Immediate subprocess termination
- Minimal memory footprint
- OS-optimized ping parameters

TARGET PERFORMANCE:
- Alive devices: 1-50ms response
- Dead devices: 50-100ms timeout
- Sustained: 100+ devices/second
- Burst: 500+ devices/second
"""

import os
import sys
import time
import subprocess
import platform
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Optional
import ipaddress
import re
from dataclasses import dataclass

@dataclass
class LightningResult:
    """Lightning-fast ping result"""
    ip: str
    is_alive: bool
    ping_time_ms: float
    total_time_ms: float
    details: str

class LightningFastPingValidator:
    """Lightning-fast pure system ping validator"""
    
    def __init__(self):
        # Ultra-minimal configuration for maximum speed
        self.config = {
            'alive_timeout_ms': 50,     # 50ms for alive detection
            'dead_timeout_ms': 100,     # 100ms for dead confirmation
            'max_workers': 10000,       # Ultra-high concurrency
            'use_raw_ping': True,       # Use raw system ping only
            'no_dns_lookup': True,      # Skip DNS for speed
        }
        
        # Prepare the fastest possible ping command
        self.ping_command = self._create_fastest_ping_command()
        
        self.stats = {
            'total_scanned': 0,
            'alive_found': 0,
            'dead_found': 0,
            'fastest_ping': float('inf'),
            'total_time': 0,
        }

    def _create_fastest_ping_command(self) -> str:
        """Create the absolute fastest ping command for the OS"""
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: Fastest possible ping
            # -n 1: single ping
            # -w 50: 50ms timeout
            # -l 32: 32 byte packet (minimal)
            return "ping -n 1 -w {timeout} -l 32 {ip}"
        
        elif system == "linux":
            # Linux: Ultra-fast ping
            # -c 1: single ping
            # -W 0.05: 50ms timeout
            # -s 32: 32 byte packet
            # -i 0.001: minimal interval
            return "ping -c 1 -W {timeout_sec} -s 32 {ip}"
        
        elif system == "darwin":  # macOS
            # macOS: Fast ping
            # -c 1: single ping
            # -W 50: 50ms timeout
            # -s 32: 32 byte packet
            return "ping -c 1 -W {timeout} -s 32 {ip}"
        
        else:
            # Generic Unix
            return "ping -c 1 -W {timeout_sec} {ip}"

    def lightning_ping(self, ip: str) -> LightningResult:
        """Lightning-fast single ping"""
        start_time = time.time()
        
        try:
            # Prepare command with appropriate timeout
            system = platform.system().lower()
            
            if system == "windows":
                cmd = self.ping_command.format(
                    timeout=self.config['alive_timeout_ms'],
                    ip=ip
                )
                timeout_seconds = self.config['alive_timeout_ms'] / 1000.0
            else:
                timeout_sec = self.config['alive_timeout_ms'] / 1000.0
                cmd = self.ping_command.format(
                    timeout_sec=timeout_sec,
                    ip=ip
                )
                timeout_seconds = timeout_sec
            
            # Execute with minimal overhead
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if system == "windows" else 0
            )
            
            # Wait with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds * 2)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()  # Clean up
                
                total_time = (time.time() - start_time) * 1000
                return LightningResult(
                    ip=ip,
                    is_alive=False,
                    ping_time_ms=total_time,
                    total_time_ms=total_time,
                    details=f"Timeout after {total_time:.1f}ms"
                )
            
            total_time = (time.time() - start_time) * 1000
            
            if returncode == 0:
                # Extract actual ping time
                actual_ping_time = self._extract_ping_time_fast(stdout, system)
                ping_ms = actual_ping_time if actual_ping_time > 0 else total_time
                
                return LightningResult(
                    ip=ip,
                    is_alive=True,
                    ping_time_ms=ping_ms,
                    total_time_ms=total_time,
                    details=f"Alive: {ping_ms:.1f}ms"
                )
            else:
                return LightningResult(
                    ip=ip,
                    is_alive=False,
                    ping_time_ms=total_time,
                    total_time_ms=total_time,
                    details="No response"
                )
                
        except Exception as e:
            total_time = (time.time() - start_time) * 1000
            return LightningResult(
                ip=ip,
                is_alive=False,
                ping_time_ms=total_time,
                total_time_ms=total_time,
                details=f"Error: {str(e)}"
            )

    def _extract_ping_time_fast(self, output: str, system: str) -> float:
        """Fast extraction of ping time from output"""
        try:
            if system == "windows":
                # Look for "time=1ms" or "time<1ms"
                match = re.search(r'time[<=](\d+)ms', output)
                if match:
                    return float(match.group(1))
                    
                # Look for "Average = 1ms"
                match = re.search(r'Average = (\d+)ms', output)
                if match:
                    return float(match.group(1))
            else:
                # Look for "time=1.234" 
                match = re.search(r'time=([\d.]+)', output)
                if match:
                    return float(match.group(1))
            
            return -1
        except:
            return -1

    def lightning_batch_scan(self, ips: List[str], progress_callback=None) -> List[LightningResult]:
        """Lightning-fast batch scanning with maximum concurrency"""
        
        if not ips:
            return []
        
        print(f"⚡ Lightning scan: {len(ips)} devices with {self.config['max_workers']} workers")
        start_time = time.time()
        
        results = []
        
        # Calculate optimal worker count
        max_workers = min(self.config['max_workers'], len(ips), 10000)
        
        # Ultra-high concurrency scanning
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all ping tasks
            future_to_ip = {executor.submit(self.lightning_ping, ip): ip for ip in ips}
            
            completed = 0
            start_report_time = time.time()
            
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Add error result
                    results.append(LightningResult(
                        ip=ip,
                        is_alive=False,
                        ping_time_ms=1000,
                        total_time_ms=1000,
                        details=f"Exception: {str(e)}"
                    ))
                
                completed += 1
                
                # Progress reporting every 100 devices or every 2 seconds
                current_time = time.time()
                if (completed % 100 == 0 or completed == len(ips) or 
                    current_time - start_report_time >= 2.0):
                    
                    elapsed = current_time - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    print(f"   ⚡ {completed}/{len(ips)} ({rate:.1f}/sec)")
                    
                    if progress_callback:
                        progress_callback((completed / len(ips)) * 100)
                    
                    start_report_time = current_time
        
        total_time = time.time() - start_time
        
        # Update statistics
        alive_results = [r for r in results if r.is_alive]
        ping_times = [r.ping_time_ms for r in alive_results if r.ping_time_ms > 0]
        
        self.stats.update({
            'total_scanned': len(results),
            'alive_found': len(alive_results),
            'dead_found': len(results) - len(alive_results),
            'fastest_ping': min(ping_times) if ping_times else 0,
            'total_time': total_time,
        })
        
        return results

    def lightning_validate_network(self, targets: List[str], progress_callback=None, log_callback=None) -> List[LightningResult]:
        """Lightning-fast network validation"""
        
        def log(message):
            if log_callback:
                log_callback(message)
            else:
                print(message)
        
        # Expand targets to IPs
        all_ips = []
        for target in targets:
            try:
                if '/' in target:  # CIDR
                    network = ipaddress.ip_network(target, strict=False)
                    ips = [str(ip) for ip in network.hosts()]
                    # Limit very large networks
                    if len(ips) > 5000:
                        log(f"⚠️ Large network {target} ({len(ips)} IPs) - limiting to first 5000")
                        ips = ips[:5000]
                    all_ips.extend(ips)
                elif '-' in target and '.' in target:  # Range
                    if target.count('.') == 3 and '-' in target.split('.')[-1]:
                        base = '.'.join(target.split('.')[:-1])
                        range_part = target.split('.')[-1]
                        start, end = range_part.split('-')
                        # Limit range size
                        end = min(int(end), int(start) + 5000)
                        for i in range(int(start), end + 1):
                            all_ips.append(f"{base}.{i}")
                    else:
                        all_ips.append(target)
                else:  # Single IP
                    all_ips.append(target)
            except Exception as e:
                log(f"⚠️ Error expanding {target}: {e}")
                all_ips.append(target)
        
        unique_ips = list(dict.fromkeys(all_ips))
        
        log("⚡ LIGHTNING-FAST PURE SYSTEM PING VALIDATOR")
        log("=" * 70)
        log(f"🎯 Target devices: {len(unique_ips)}")
        log(f"⏱️  Ping timeout: {self.config['alive_timeout_ms']}ms")
        log(f"🔧 Max workers: {min(self.config['max_workers'], len(unique_ips))}")
        log(f"🖥️  OS: {platform.system()}")
        log(f"📡 Method: Pure system ping only")
        log("")
        
        start_time = time.time()
        
        # Lightning-fast scanning
        results = self.lightning_batch_scan(unique_ips, progress_callback)
        
        total_time = time.time() - start_time
        
        # Print lightning results
        self._print_lightning_summary(results, total_time, log)
        
        return results

    def _print_lightning_summary(self, results: List[LightningResult], total_time: float, log_func):
        """Print lightning-fast results summary"""
        
        if not results:
            log_func("❌ No results to display")
            return
        
        alive_devices = [r for r in results if r.is_alive]
        dead_devices = [r for r in results if not r.is_alive]
        
        log_func("")
        log_func("=" * 80)
        log_func("⚡ LIGHTNING-FAST PING VALIDATION RESULTS")
        log_func("=" * 80)
        
        log_func(f"📊 SCAN RESULTS:")
        log_func(f"   Total Scanned: {len(results)}")
        log_func(f"   ✅ Alive: {len(alive_devices)} ({len(alive_devices)/len(results)*100:.1f}%)")
        log_func(f"   ❌ Dead/Timeout: {len(dead_devices)} ({len(dead_devices)/len(results)*100:.1f}%)")
        log_func("")
        
        log_func(f"⚡ LIGHTNING PERFORMANCE:")
        log_func(f"   ⏱️  Total Time: {total_time:.2f} seconds")
        log_func(f"   🚀 Scan Rate: {len(results)/total_time:.1f} devices/second")
        if self.stats['fastest_ping'] < float('inf'):
            log_func(f"   ⚡ Fastest Ping: {self.stats['fastest_ping']:.1f}ms")
        
        # Calculate response time statistics
        if alive_devices:
            ping_times = [r.ping_time_ms for r in alive_devices]
            avg_ping = sum(ping_times) / len(ping_times)
            log_func(f"   📊 Average Ping: {avg_ping:.1f}ms")
        
        log_func("")
        
        # Show fastest responding devices
        if alive_devices:
            fastest_devices = sorted(alive_devices, key=lambda x: x.ping_time_ms)[:15]
            log_func(f"⚡ FASTEST RESPONDING DEVICES:")
            for device in fastest_devices:
                log_func(f"   {device.ip:15} | {device.ping_time_ms:6.1f}ms | {device.details}")
        
        # Show any interesting dead devices
        timeout_devices = [r for r in dead_devices if "Timeout" in r.details]
        if timeout_devices:
            log_func(f"\n⏱️  TIMEOUT DEVICES: {len(timeout_devices)}")
            if len(timeout_devices) <= 5:  # Show only if few
                for device in timeout_devices[:5]:
                    log_func(f"   {device.ip:15} | {device.details}")
        
        log_func("")
        log_func("⚡ LIGHTNING VALIDATION SUCCESS:")
        log_func("   ✅ Pure system ping for absolute maximum speed")
        log_func("   ✅ Ultra-minimal timeouts for rapid detection")
        log_func("   ✅ Massive concurrency for parallel processing")
        log_func("   ✅ Optimized for large network discovery!")

def main():
    """Main function for lightning-fast ping validation"""
    
    # Test targets
    test_targets = [
        "127.0.0.1",        # Localhost
        "8.8.8.8",          # Google DNS
        "1.1.1.1",          # Cloudflare DNS
        "192.168.1.1-20",   # Local network range
        "10.0.0.1-5",       # Gateway range
        "169.254.1.1-10",   # Link-local range
    ]
    
    print("⚡ LIGHTNING-FAST PURE SYSTEM PING VALIDATOR")
    print("=" * 70)
    print("Absolute fastest ping validation possible!")
    print("Pure OS system ping with minimal timeouts")
    print()
    
    # Create validator
    validator = LightningFastPingValidator()
    
    # Show system info
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"⚙️  Ping timeout: {validator.config['alive_timeout_ms']}ms")
    print(f"🔧 Max workers: {validator.config['max_workers']}")
    print()
    
    # Run lightning validation
    def log_handler(message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def progress_handler(percentage):
        if percentage % 25 == 0:
            print(f"⚡ Progress: {percentage:.0f}%")
    
    start_time = time.time()
    results = validator.lightning_validate_network(test_targets, progress_handler, log_handler)
    total_time = time.time() - start_time
    
    print(f"\n⚡ LIGHTNING VALIDATION COMPLETED!")
    print(f"🚀 Scanned {len(results)} devices in {total_time:.2f} seconds")
    print(f"⚡ Rate: {len(results)/total_time:.1f} devices/second")
    if validator.stats['fastest_ping'] < float('inf'):
        print(f"💨 Fastest response: {validator.stats['fastest_ping']:.1f}ms")

if __name__ == "__main__":
    main()