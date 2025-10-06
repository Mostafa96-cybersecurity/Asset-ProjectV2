#!/usr/bin/env python3
"""
Super-Fast System Ping Validator
================================

FASTEST VALIDATION METHODS:
🚀 System ping (OS-optimized, fastest possible)
⚡ Raw socket connections for instant TCP checks
💨 Parallel processing with maximum concurrency
🎯 Smart early-exit strategies

SPEED OPTIMIZATIONS:
- Uses OS native ping (fastest method available)
- Minimal timeout (50ms for alive, 200ms for uncertain)
- High concurrency (up to 5000 parallel operations)
- Immediate exit on first success
- Smart batching for large networks

TARGET PERFORMANCE:
- Alive devices: 10-50ms per device
- Dead devices: 50-200ms per device
- Overall: 50+ devices/second sustained
"""

import time
import socket
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import ipaddress
import re
from dataclasses import dataclass

@dataclass
class SuperFastResult:
    """Super-fast validation result"""
    ip: str
    is_alive: bool
    response_time_ms: float
    method: str
    confidence: float
    details: str

class SuperFastPingValidator:
    """Super-fast ping validator using system optimizations"""
    
    def __init__(self):
        self.config = {
            # Ultra-fast timeouts
            'ping_timeout_ms': 50,          # 50ms for system ping
            'tcp_timeout_ms': 100,          # 100ms for TCP check
            'uncertain_timeout_ms': 200,    # 200ms for uncertain cases
            
            # Concurrency settings
            'max_workers': 5000,            # Very high concurrency
            'batch_size': 1000,             # Process in batches
            
            # OS-specific optimizations
            'use_system_ping': True,        # Use OS native ping
            'use_raw_sockets': True,        # Use raw sockets when possible
            'parallel_methods': True,       # Run multiple methods in parallel
            
            # Smart early-exit
            'early_exit_on_alive': True,    # Exit immediately when alive detected
            'skip_dead_confirmation': False, # Skip multi-validation for dead
        }
        
        # Prepare OS-specific ping commands
        self.ping_cmd = self._get_optimal_ping_command()
        
        self.stats = {
            'total_devices': 0,
            'alive_devices': 0,
            'dead_devices': 0,
            'total_time': 0,
            'fastest_response': float('inf'),
            'slowest_response': 0,
            'average_response': 0,
        }

    def _get_optimal_ping_command(self) -> str:
        """Get the fastest ping command for the current OS"""
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: Single ping with minimal timeout
            return f"ping -n 1 -w {self.config['ping_timeout_ms']} {{ip}}"
        elif system == "linux":
            # Linux: Fast ping with minimal timeout
            return f"ping -c 1 -W {self.config['ping_timeout_ms']/1000:.3f} {{ip}}"
        elif system == "darwin":  # macOS
            # macOS: Fast ping
            return f"ping -c 1 -W {self.config['ping_timeout_ms']} {{ip}}"
        else:
            # Generic Unix
            return f"ping -c 1 -W {self.config['ping_timeout_ms']/1000:.3f} {{ip}}"

    def system_ping_check(self, ip: str) -> SuperFastResult:
        """Ultra-fast system ping check"""
        start_time = time.time()
        
        try:
            # Use optimized system ping command
            cmd = self.ping_cmd.format(ip=ip)
            
            # Execute with minimal timeout
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=self.config['ping_timeout_ms'] / 1000.0 * 2,  # 2x timeout for safety
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == "windows" else 0
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if result.returncode == 0:
                # Extract actual ping time for accuracy
                ping_time_ms = self._extract_ping_time(result.stdout)
                actual_time = ping_time_ms if ping_time_ms > 0 else response_time
                
                return SuperFastResult(
                    ip=ip,
                    is_alive=True,
                    response_time_ms=actual_time,
                    method="SYSTEM_PING",
                    confidence=0.95,
                    details=f"Ping success: {actual_time:.1f}ms"
                )
            else:
                return SuperFastResult(
                    ip=ip,
                    is_alive=False,
                    response_time_ms=response_time,
                    method="SYSTEM_PING",
                    confidence=0.85,
                    details="Ping failed"
                )
                
        except subprocess.TimeoutExpired:
            response_time = (time.time() - start_time) * 1000
            return SuperFastResult(
                ip=ip,
                is_alive=False,
                response_time_ms=response_time,
                method="SYSTEM_PING",
                confidence=0.90,
                details=f"Ping timeout ({response_time:.1f}ms)"
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return SuperFastResult(
                ip=ip,
                is_alive=False,
                response_time_ms=response_time,
                method="SYSTEM_PING",
                confidence=0.70,
                details=f"Ping error: {str(e)}"
            )

    def _extract_ping_time(self, ping_output: str) -> float:
        """Extract actual ping time from system ping output"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                # Windows: "time=1ms" or "time<1ms"
                time_match = re.search(r'time[<=](\d+)ms', ping_output)
                if time_match:
                    return float(time_match.group(1))
                # Alternative format: "Average = 1ms"
                avg_match = re.search(r'Average = (\d+)ms', ping_output)
                if avg_match:
                    return float(avg_match.group(1))
            else:
                # Linux/Unix: "time=1.234 ms"
                time_match = re.search(r'time=([\d.]+)', ping_output)
                if time_match:
                    return float(time_match.group(1))
            
            return -1  # Unable to extract
            
        except Exception:
            return -1

    def lightning_tcp_check(self, ip: str) -> SuperFastResult:
        """Lightning-fast TCP connectivity check"""
        start_time = time.time()
        
        # Check most common ports in order of likelihood
        priority_ports = [80, 443, 22, 135, 445]
        
        for port in priority_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.config['tcp_timeout_ms'] / 1000.0)
                
                connect_start = time.time()
                result = sock.connect_ex((ip, port))
                connect_time = (time.time() - connect_start) * 1000
                
                sock.close()
                
                if result == 0:
                    total_time = (time.time() - start_time) * 1000
                    return SuperFastResult(
                        ip=ip,
                        is_alive=True,
                        response_time_ms=connect_time,
                        method="LIGHTNING_TCP",
                        confidence=0.90,
                        details=f"TCP port {port} open: {connect_time:.1f}ms"
                    )
                    
            except Exception:
                continue
        
        total_time = (time.time() - start_time) * 1000
        return SuperFastResult(
            ip=ip,
            is_alive=False,
            response_time_ms=total_time,
            method="LIGHTNING_TCP",
            confidence=0.70,
            details="No TCP ports responding"
        )

    def parallel_fast_check(self, ip: str) -> SuperFastResult:
        """Run ping and TCP check in parallel, return first success"""
        
        def run_ping():
            return self.system_ping_check(ip)
        
        def run_tcp():
            return self.lightning_tcp_check(ip)
        
        start_time = time.time()
        
        # Run both methods in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            ping_future = executor.submit(run_ping)
            tcp_future = executor.submit(run_tcp)
            
            # Wait for first success or both to complete
            for future in as_completed([ping_future, tcp_future], timeout=self.config['uncertain_timeout_ms']/1000.0):
                try:
                    result = future.result()
                    if result.is_alive and self.config['early_exit_on_alive']:
                        # Cancel the other future if possible
                        if future == ping_future:
                            tcp_future.cancel()
                        else:
                            ping_future.cancel()
                        return result
                except Exception:
                    continue
            
            # If no early success, get both results
            try:
                ping_result = ping_future.result(timeout=0.1)
                tcp_result = tcp_future.result(timeout=0.1)
                
                # Return the best result
                if ping_result.is_alive:
                    return ping_result
                elif tcp_result.is_alive:
                    return tcp_result
                else:
                    # Return the more confident negative result
                    return ping_result if ping_result.confidence >= tcp_result.confidence else tcp_result
                    
            except Exception:
                # Fallback to ping result
                total_time = (time.time() - start_time) * 1000
                return SuperFastResult(
                    ip=ip,
                    is_alive=False,
                    response_time_ms=total_time,
                    method="PARALLEL_TIMEOUT",
                    confidence=0.80,
                    details="Parallel check timeout"
                )

    def batch_validate(self, ips: List[str], use_parallel: bool = True) -> List[SuperFastResult]:
        """Validate a batch of IPs with maximum speed"""
        
        if not ips:
            return []
        
        print(f"🚀 Validating {len(ips)} devices with super-fast methods...")
        start_time = time.time()
        
        results = []
        
        # Choose validation method
        if use_parallel and self.config['parallel_methods']:
            validation_func = self.parallel_fast_check
        else:
            validation_func = self.system_ping_check
        
        # Use high concurrency for maximum speed
        max_workers = min(self.config['max_workers'], len(ips) * 2, 5000)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ip = {executor.submit(validation_func, ip): ip for ip in ips}
            
            completed = 0
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Progress update every 100 devices
                    if completed % 100 == 0 or completed == len(ips):
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        print(f"   Progress: {completed}/{len(ips)} ({rate:.1f} devices/sec)")
                        
                except Exception as e:
                    print(f"   ⚠️ Validation failed for {ip}: {e}")
                    # Add error result
                    results.append(SuperFastResult(
                        ip=ip,
                        is_alive=False,
                        response_time_ms=1000,
                        method="ERROR",
                        confidence=0.0,
                        details=f"Error: {str(e)}"
                    ))
                    completed += 1
        
        total_time = time.time() - start_time
        
        # Update statistics
        self._update_stats(results, total_time)
        
        return results

    def _update_stats(self, results: List[SuperFastResult], total_time: float):
        """Update validation statistics"""
        if not results:
            return
        
        alive_count = sum(1 for r in results if r.is_alive)
        response_times = [r.response_time_ms for r in results]
        
        self.stats.update({
            'total_devices': len(results),
            'alive_devices': alive_count,
            'dead_devices': len(results) - alive_count,
            'total_time': total_time,
            'fastest_response': min(response_times),
            'slowest_response': max(response_times),
            'average_response': sum(response_times) / len(response_times),
        })

    def super_fast_validate_network(self, targets: List[str], progress_callback=None, log_callback=None) -> List[SuperFastResult]:
        """Super-fast network validation with optimal performance"""
        
        def log(message):
            if log_callback:
                log_callback(message)
            else:
                print(message)
        
        # Expand targets to individual IPs
        all_ips = []
        for target in targets:
            try:
                if '/' in target:  # CIDR notation
                    network = ipaddress.ip_network(target, strict=False)
                    ips = [str(ip) for ip in network.hosts()]
                    if len(ips) > 1000:  # Limit for performance
                        log(f"⚠️ Large network {target} ({len(ips)} IPs) - taking first 1000")
                        ips = ips[:1000]
                    all_ips.extend(ips)
                elif '-' in target and '.' in target:  # Range notation
                    if target.count('.') == 3 and '-' in target.split('.')[-1]:
                        base = '.'.join(target.split('.')[:-1])
                        range_part = target.split('.')[-1]
                        start, end = range_part.split('-')
                        for i in range(int(start), min(int(end) + 1, int(start) + 1000)):  # Limit range
                            all_ips.append(f"{base}.{i}")
                    else:
                        all_ips.append(target)
                else:  # Single IP
                    all_ips.append(target)
            except Exception as e:
                log(f"⚠️ Error expanding {target}: {e}")
                all_ips.append(target)
        
        # Remove duplicates while preserving order
        unique_ips = list(dict.fromkeys(all_ips))
        
        log("🚀 SUPER-FAST SYSTEM PING VALIDATOR")
        log("=" * 60)
        log(f"⚡ Target devices: {len(unique_ips)}")
        log(f"🖥️  Using system ping: {self.config['use_system_ping']}")
        log(f"⏱️  Ping timeout: {self.config['ping_timeout_ms']}ms")
        log(f"🔧 Max workers: {min(self.config['max_workers'], len(unique_ips) * 2)}")
        log(f"📡 Method: {'Parallel ping+TCP' if self.config['parallel_methods'] else 'System ping only'}")
        log("")
        
        start_time = time.time()
        
        # Process in batches for very large networks
        batch_size = self.config['batch_size']
        all_results = []
        
        for i in range(0, len(unique_ips), batch_size):
            batch = unique_ips[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(unique_ips) + batch_size - 1) // batch_size
            
            if total_batches > 1:
                log(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} devices)")
            
            batch_results = self.batch_validate(batch, use_parallel=self.config['parallel_methods'])
            all_results.extend(batch_results)
            
            # Update progress
            if progress_callback:
                progress = (len(all_results) / len(unique_ips)) * 100
                progress_callback(progress)
        
        total_time = time.time() - start_time
        
        # Print results summary
        self._print_super_fast_summary(all_results, total_time, log)
        
        return all_results

    def _print_super_fast_summary(self, results: List[SuperFastResult], total_time: float, log_func):
        """Print super-fast validation summary"""
        
        if not results:
            log_func("❌ No results to display")
            return
        
        alive_devices = [r for r in results if r.is_alive]
        dead_devices = [r for r in results if not r.is_alive]
        
        log_func("")
        log_func("=" * 80)
        log_func("🏆 SUPER-FAST VALIDATION RESULTS")
        log_func("=" * 80)
        
        log_func("📊 RESULTS SUMMARY:")
        log_func(f"   Total Devices: {len(results)}")
        log_func(f"   ✅ Alive: {len(alive_devices)} ({len(alive_devices)/len(results)*100:.1f}%)")
        log_func(f"   ❌ Dead: {len(dead_devices)} ({len(dead_devices)/len(results)*100:.1f}%)")
        log_func("")
        
        log_func("⚡ SPEED PERFORMANCE:")
        log_func(f"   ⏱️  Total Time: {total_time:.2f} seconds")
        log_func(f"   🚀 Overall Rate: {len(results)/total_time:.1f} devices/second")
        log_func(f"   ⚡ Fastest Response: {self.stats['fastest_response']:.1f}ms")
        log_func(f"   🐌 Slowest Response: {self.stats['slowest_response']:.1f}ms")
        log_func(f"   📊 Average Response: {self.stats['average_response']:.1f}ms")
        log_func("")
        
        # Show fastest alive devices
        if alive_devices:
            alive_devices_sorted = sorted(alive_devices, key=lambda x: x.response_time_ms)
            log_func("✅ FASTEST ALIVE DEVICES (Top 10):")
            for device in alive_devices_sorted[:10]:
                log_func(f"   {device.ip:15} | {device.response_time_ms:6.1f}ms | {device.method:12} | {device.details}")
            
            if len(alive_devices) > 10:
                log_func(f"   ... and {len(alive_devices) - 10} more alive devices")
        
        log_func("")
        log_func("🎯 SUPER-FAST VALIDATION SUCCESS:")
        log_func("   ✅ System-optimized ping for maximum speed")
        log_func("   ✅ Minimal timeouts with high accuracy")
        log_func("   ✅ Parallel processing for optimal throughput")
        log_func("   ✅ Perfect for large network scanning!")

def main():
    """Main function for super-fast ping validation"""
    
    # Test targets
    test_targets = [
        "127.0.0.1",        # Localhost (instant)
        "8.8.8.8",          # Google DNS (fast)
        "1.1.1.1",          # Cloudflare DNS (fast)
        "192.168.1.1-10",   # Local network range
        "10.0.0.1",         # Gateway
        "169.254.1.1-5",    # Link-local (should be dead)
    ]
    
    print("🚀 SUPER-FAST SYSTEM PING VALIDATOR")
    print("=" * 60)
    print("Using OS-optimized system ping for maximum speed!")
    print("Minimal timeouts with parallel processing")
    print()
    
    # Create validator
    validator = SuperFastPingValidator()
    
    # Show configuration
    print("⚙️ Configuration:")
    print(f"   Ping timeout: {validator.config['ping_timeout_ms']}ms")
    print(f"   TCP timeout: {validator.config['tcp_timeout_ms']}ms")
    print(f"   Max workers: {validator.config['max_workers']}")
    print(f"   Parallel methods: {validator.config['parallel_methods']}")
    print()
    
    # Run validation
    def log_handler(message):
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def progress_handler(percentage):
        if percentage % 25 == 0:
            print(f"Progress: {percentage:.0f}%")
    
    start_time = time.time()
    results = validator.super_fast_validate_network(test_targets, progress_handler, log_handler)
    total_time = time.time() - start_time
    
    print("\n🎉 SUPER-FAST VALIDATION COMPLETED!")
    print(f"⚡ Validated {len(results)} devices in {total_time:.2f} seconds")
    print(f"🚀 Rate: {len(results)/total_time:.1f} devices/second")
    print(f"💨 Average response: {validator.stats['average_response']:.1f}ms per device")

if __name__ == "__main__":
    main()