
# COLLECTION TROUBLESHOOTING GUIDE
================================

## Common Issues and Solutions

### 1. NMAP Not Found
**Issue:** "nmap program was not found in path"
**Solutions:**
- Install NMAP: `winget install nmap`
- Download from: https://nmap.org/download.html
- Add NMAP to system PATH
- Use fallback scanning (automatic)

### 2. WMI Collection Fails
**Issue:** "All collection methods failed"
**Reasons:**
- Target is not Windows
- Firewall blocking WMI
- Authentication failure
- Admin rights required

**Solutions:**
- Ensure Windows credentials are correct
- Run as administrator
- Check Windows firewall settings
- Verify WMI service is running

### 3. SSH Collection Fails
**Issue:** SSH connection refused
**Reasons:**
- SSH service not running
- Wrong port (default 22)
- Authentication failure
- Firewall blocking

**Solutions:**
- Verify SSH service is enabled
- Check correct port number
- Verify SSH credentials
- Test manual SSH connection

### 4. SNMP Collection Fails
**Issue:** No SNMP response
**Reasons:**
- SNMP service disabled
- Wrong community string
- SNMP version mismatch
- Firewall blocking port 161

**Solutions:**
- Enable SNMP service on target
- Verify community string ("public" default)
- Try different SNMP versions
- Check firewall rules

### 5. HTTP Detection Fails
**Issue:** No web services found
**Reasons:**
- No web server running
- Non-standard ports
- HTTPS only
- Firewall blocking

**Solutions:**
- Check if web server is running
- Try common ports: 80, 443, 8080, 8443
- Verify SSL certificates
- Check firewall settings

## Best Practices

1. **Network Preparation:**
   - Ensure network connectivity
   - Configure appropriate credentials
   - Check firewall rules
   - Verify service availability

2. **Credential Management:**
   - Use service accounts
   - Rotate credentials regularly
   - Test credentials manually first
   - Use least privilege principle

3. **Performance Optimization:**
   - Limit concurrent connections
   - Use appropriate timeouts
   - Monitor resource usage
   - Schedule scans during off-hours

4. **Troubleshooting Steps:**
   1. Test network connectivity (ping)
   2. Test individual collection methods
   3. Check logs for specific errors
   4. Verify target system configuration
   5. Test with manual tools first

## Expected Success Rates

- **Ping Detection:** 90-95% (for reachable devices)
- **OS Detection:** 70-80% (depends on NMAP availability)
- **WMI Collection:** 60-70% (Windows only, auth dependent)
- **SSH Collection:** 40-60% (Linux/Unix, auth dependent)
- **SNMP Collection:** 30-50% (network devices, config dependent)
- **HTTP Detection:** 20-40% (web servers only)

Note: Low success rates are normal for security reasons.
Many devices block or restrict these collection methods.
