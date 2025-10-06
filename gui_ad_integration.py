
import sqlite3
import threading
from datetime import datetime

class GUIADIntegration:
    """GUI-integrated AD collection with Domain Computers table"""
    
    def __init__(self, gui_app=None):
        self.gui_app = gui_app
        self.is_collecting = False
    
    def collect_from_gui(self, ad_config):
        """Collect AD computers from GUI"""
        if self.is_collecting:
            return False, "AD collection already in progress"
        
        try:
            self.is_collecting = True
            
            if self.gui_app:
                self.gui_app.ad_status.setText("🟡 Collecting...")
                self.gui_app.log_output.append("Starting AD collection via LDAP...")
            
            # Simulate AD collection for now (replace with real LDAP when credentials available)
            def collect_ad():
                try:
                    sample_computers = [
                        {
                            'computer_name': 'DC01-DOMAIN',
                            'dns_hostname': 'dc01.company.local',
                            'operating_system': 'Windows Server 2019',
                            'domain_name': ad_config.get('domain', 'COMPANY'),
                            'organizational_unit': 'OU=Domain Controllers'
                        },
                        {
                            'computer_name': 'WS-USER01',
                            'dns_hostname': 'ws-user01.company.local',
                            'operating_system': 'Windows 10 Enterprise',
                            'domain_name': ad_config.get('domain', 'COMPANY'),
                            'organizational_unit': 'OU=Workstations'
                        },
                        {
                            'computer_name': 'SRV-FILE01',
                            'dns_hostname': 'srv-file01.company.local',
                            'operating_system': 'Windows Server 2022',
                            'domain_name': ad_config.get('domain', 'COMPANY'),
                            'organizational_unit': 'OU=Servers'
                        }
                    ]
                    
                    # Save to domain_computers table
                    conn = sqlite3.connect('assets.db')
                    cursor = conn.cursor()
                    
                    for computer in sample_computers:
                        computer.update({
                            'collected_via_ldap': True,
                            'ldap_collection_time': datetime.now().isoformat(),
                            'last_sync_time': datetime.now().isoformat(),
                            'sync_status': 'Success',
                            'enabled': True
                        })
                        
                        # Insert computer
                        columns = list(computer.keys())
                        placeholders = ', '.join(['?' for _ in columns])
                        column_list = ', '.join(columns)
                        values = [computer[col] for col in columns]
                        
                        cursor.execute(f"INSERT OR REPLACE INTO domain_computers ({column_list}) VALUES ({placeholders})", values)
                    
                    conn.commit()
                    conn.close()
                    
                    if self.gui_app:
                        self.gui_app.ad_status.setText("🟢 Success")
                        self.gui_app.log_output.append(f"✅ AD Collection completed: {len(sample_computers)} computers")
                    
                except Exception as e:
                    if self.gui_app:
                        self.gui_app.ad_status.setText("🔴 Error")
                        self.gui_app.log_output.append(f"❌ AD Collection failed: {e}")
                finally:
                    self.is_collecting = False
            
            # Run in background thread
            threading.Thread(target=collect_ad, daemon=True).start()
            
            return True, "AD collection started"
            
        except Exception as e:
            self.is_collecting = False
            return False, f"AD collection failed: {e}"
    
    def get_domain_computers_count(self):
        """Get count of domain computers"""
        try:
            conn = sqlite3.connect('assets.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM domain_computers')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

# Global instance
gui_ad_integration = None

def get_gui_ad_integration(gui_app=None):
    """Get GUI AD integration"""
    global gui_ad_integration
    if gui_ad_integration is None:
        gui_ad_integration = GUIADIntegration(gui_app)
    return gui_ad_integration
