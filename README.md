# Asset Management System - Enhanced Edition

A comprehensive asset management system with advanced features for network device discovery, collection, and management. This enhanced edition includes ultra-fast collection, thread-safe UI, automatic scanning, and massive network protection.

## 🚀 Features

### Core Functionality
- **Ultra-Fast Device Collection**: High-performance network device discovery and data collection
- **Thread-Safe UI**: Prevents application hanging during large-scale operations
- **Automatic Scanning**: Scheduled and automated network scanning capabilities
- **Massive Network Protection**: Handles 3+ networks without UI freezing
- **Duplicate Prevention**: Intelligent duplicate detection and cleanup

### Enhanced UI System
- **6-Layer UI Responsiveness**: Multi-layered protection against UI hanging
- **Emergency UI Recovery**: Guaranteed responsive interface even during intensive operations
- **Instant UI Fixes**: Real-time UI responsiveness enhancements
- **Process-Based Collection**: Separate processes for heavy operations
- **Critical Threading Protection**: Advanced threading management

### Data Management
- **SQLite Database Integration**: Robust data storage with backup capabilities
- **Active Directory Integration**: Seamless AD integration for enterprise environments
- **Department Management**: Organize assets by departments and organizational units
- **Collection Limiting**: Smart collection limits to prevent system overload

## 📋 Prerequisites

- Python 3.13+
- PyQt6
- Windows OS (recommended)
- Git (for version control)

## 🛠️ Installation

### Quick Setup
1. Clone the repository:
```bash
git clone https://github.com/Mostafa96-cybersecurity/Asset-Desktop.git
cd Asset-Desktop
```

2. Run the automated setup script:
```powershell
# Open PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned
.\setup.ps1
```

3. Activate virtual environment and run:
```powershell
.\.venv\Scripts\activate
python gui/app.py
```

### Manual Setup
If you prefer manual setup:

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install PyQt6 requests psutil wmi winshell

# Run the application
python gui/app.py
```

## 🚀 How to Run

### Desktop Application
```bash
python gui/app.py
```

### Web Interface
```bash
python production_web_service.py
```
Then open http://localhost:5000 in your browser.

## 📁 Project Structure

```
Asset-Desktop/
├── gui/                          # GUI modules
│   ├── app.py                   # Main application interface
│   ├── enhanced_app.py          # Enhanced GUI features
│   ├── thread_safe_enhancement.py # Thread safety improvements
│   └── department_management.py # Department management UI
├── core/                        # Core business logic
│   ├── worker.py               # Worker threads
│   ├── collector.py            # Collection engines
│   └── logic.py                # Business logic
├── collectors/                  # Data collectors
│   ├── wmi_collector.py        # WMI-based collection
│   ├── ssh_collector.py        # SSH-based collection
│   └── snmp_collector.py       # SNMP-based collection
├── tools/                       # Utility tools
├── templates/                   # Web templates
├── ultra_fast_collector.py     # Core collection engine
├── automatic_scanner.py        # Automated scanning system
├── massive_scan_protection.py  # Large network protection
└── assets.db                   # SQLite database
```

## 🔧 Configuration

### Automatic Scanning
Configure automatic scanning in `automatic_scanner_config.json`:
```json
{
    "scan_interval": 3600,
    "enabled_networks": ["192.168.1.0/24"],
    "max_concurrent_scans": 5
}
```

### Network Profiles
Set up network profiles in `network_profiles.json`:
```json
{
    "profiles": [
        {
            "name": "Office Network",
            "network": "192.168.1.0/24",
            "credentials": "default"
        }
    ]
}
```

## 🚀 Key Components

### Ultra-Fast Collector
High-performance device collection with:
- Multi-threaded scanning
- Intelligent retry mechanisms
- Progress tracking
- Error handling

### Thread-Safe Enhancements
- UI responsiveness during operations
- Background processing
- Thread pool management
- Emergency recovery systems

### Massive Scan Protection
- Prevents UI freezing on large networks
- Smart resource management
- Automatic load balancing
- Performance monitoring

## 📊 Monitoring and Logs

The system provides comprehensive logging:
- `desktop_app.log` - Main application logs
- `enhanced_asset_collector.log` - Collection operation logs
- Real-time error monitoring dashboard

## 🔒 Security Features

- Credential management system
- Encrypted data storage
- Access control and authentication
- Audit logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Ensure Python virtual environment is properly configured
- Windows Defender may flag some network scanning operations
- Large network scans require adequate system resources

## 📞 Support

For support and questions, please open an issue in the GitHub repository.

## 🎯 Roadmap

- [ ] Linux/macOS support
- [ ] Enhanced reporting features
- [ ] Cloud integration capabilities
- [ ] Mobile app companion
- [ ] Advanced analytics dashboard

---

**Asset Management System Enhanced Edition** - Built for enterprise-scale asset management with performance and reliability in mind.
