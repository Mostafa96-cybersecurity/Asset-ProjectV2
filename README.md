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

## Prerequisites

- Python 3.13+
- PyQt6
- Windows OS (recommended)
- Git (for version control)

## Setup Instructions

A PowerShell script is provided to automate the entire setup process. This is the recommended way to prepare your environment as it ensures all dependencies are installed correctly.

1.  **Open PowerShell as an Administrator**

    Right-click the PowerShell icon and select "Run as Administrator". This is required to allow script execution if it's your first time.

2.  **Allow Script Execution (One-Time Step)**

    If you haven't run local PowerShell scripts before, you may need to change the execution policy. Run the following command and answer 'Y' or 'A' when prompted:

    ```powershell
    Set-ExecutionPolicy RemoteSigned
    ```

3.  **Run the Setup Script**

    Navigate to your project directory and run the `setup.ps1` script.

    ```powershell
    # Navigate to your project directory
    cd E:\Projects\Asset-Project-Enhanced

    # Run the setup script
    .\setup.ps1
    ```
    The script will automatically delete any old environment, create a new one, and install all dependencies.

## How to Run the Application

After the setup script completes successfully, make sure your virtual environment is active (your prompt should start with `(.venv)`). Then, run the application:

```powershell
# If your terminal session was closed, reactivate the environment first:
# .\.venv\Scripts\activate

# Run the main application
python main.py
```

This will launch the main GUI window. If the setup was successful, you will **not** see the SNMP warning message in the logs.
    ```powershell
    pip install -r requirements.txt
    ```

## How to Run the Application

Once the setup is complete, run the application from your project's root directory:

```powershell
python main.py
```

This will launch the main GUI window. If the setup was successful, you will **not** see the SNMP warning message in the logs.
