"""
Athena v2 Log Analyzer
Analyzes server log files to provide performance insights
"""

import re
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path


class LogAnalyzer:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.log_content = self.read_log()
        
    def read_log(self):
        """Read log file content"""
        with open(self.log_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_timestamps(self):
        """Extract all timestamps"""
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        timestamps = re.findall(pattern, self.log_content)
        return [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps]
    
    def get_runtime_info(self):
        """Get bot runtime information"""
        timestamps = self.extract_timestamps()
        if not timestamps:
            return None
        
        start_time = min(timestamps)
        end_time = max(timestamps)
        runtime = end_time - start_time
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'total_runtime': runtime,
            'total_hours': runtime.total_seconds() / 3600
        }
    
    def count_scans(self):
        """Count total number of scans performed"""
        pattern = r'🔍 SCANNING WATCHLIST FOR TRADING SIGNALS'
        return len(re.findall(pattern, self.log_content))
    
    def analyze_signals(self):
        """Analyze signal patterns"""
        # Extract all signal entries
        pattern = r'Signal: (HOLD|BUY|SELL) ⭐+ \((\d+) stars?\)'
        matches = re.findall(pattern, self.log_content)
        
        signal_types = Counter([m[0] for m in matches])
        star_distribution = Counter([int(m[1]) for m in matches])
        
        return {
            'total_signals_checked': len(matches),
            'signal_types': dict(signal_types),
            'star_distribution': dict(sorted(star_distribution.items()))
        }
    
    def analyze_symbols(self):
        """Analyze per-symbol activity"""
        pattern = r'Analyzing ([\w]+)\.\.\.\s+.*?Signal: (HOLD|BUY|SELL) ⭐+ \((\d+) stars?\)'
        matches = re.findall(pattern, self.log_content, re.DOTALL)
        
        symbol_data = defaultdict(lambda: {'total': 0, 'stars': []})
        
        for symbol, signal, stars in matches:
            symbol_data[symbol]['total'] += 1
            symbol_data[symbol]['stars'].append(int(stars))
        
        # Calculate averages
        for symbol in symbol_data:
            stars = symbol_data[symbol]['stars']
            symbol_data[symbol]['avg_stars'] = sum(stars) / len(stars) if stars else 0
            symbol_data[symbol]['max_stars'] = max(stars) if stars else 0
        
        return dict(symbol_data)
    
    def check_trades_executed(self):
        """Check if any trades were executed"""
        executing_pattern = r'🎯 EXECUTING TRADE'
        executed_pattern = r'Trade #\d+ executed successfully'
        
        return {
            'trades_attempted': len(re.findall(executing_pattern, self.log_content)),
            'trades_executed': len(re.findall(executed_pattern, self.log_content))
        }
    
    def check_positions(self):
        """Check position monitoring"""
        pattern = r'🎯 CHECKING POSITIONS - (\d+) open'
        matches = re.findall(pattern, self.log_content)
        
        if not matches:
            return {'position_checks': 0, 'max_concurrent': 0}
        
        position_counts = [int(m) for m in matches]
        
        return {
            'position_checks': len(matches),
            'max_concurrent': max(position_counts) if position_counts else 0,
            'avg_positions': sum(position_counts) / len(position_counts) if position_counts else 0
        }
    
    def check_errors(self):
        """Check for errors in logs"""
        error_pattern = r'ERROR - (.*?)(?=\n\d{4}-\d{2}-\d{2}|\Z)'
        warning_pattern = r'WARNING - (.*?)(?=\n\d{4}-\d{2}-\d{2}|\Z)'
        
        errors = re.findall(error_pattern, self.log_content, re.DOTALL)
        warnings = re.findall(warning_pattern, self.log_content, re.DOTALL)
        
        return {
            'error_count': len(errors),
            'warning_count': len(warnings),
            'errors': [e.strip() for e in errors[:10]],  # First 10 errors
            'warnings': [w.strip() for w in warnings[:10]]  # First 10 warnings
        }
    
    def check_connection_status(self):
        """Check Binance connection status"""
        testnet_pattern = r'Connected to Binance Futures TESTNET'
        mainnet_pattern = r'Connected to Binance Futures MAINNET'
        
        if re.search(testnet_pattern, self.log_content):
            return 'TESTNET'
        elif re.search(mainnet_pattern, self.log_content):
            return 'MAINNET ⚠️ LIVE TRADING'
        return 'UNKNOWN'
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("=" * 80)
        print("📊 ATHENA V2 LOG ANALYSIS REPORT")
        print("=" * 80)
        
        # Runtime info
        runtime = self.get_runtime_info()
        if runtime:
            print(f"\n⏰ RUNTIME INFORMATION:")
            print(f"   Start Time: {runtime['start_time']}")
            print(f"   End Time: {runtime['end_time']}")
            print(f"   Total Runtime: {runtime['total_runtime']}")
            print(f"   Hours Running: {runtime['total_hours']:.2f} hours")
        
        # Connection status
        connection = self.check_connection_status()
        print(f"\n🔌 CONNECTION STATUS: {connection}")
        
        # Scan information
        scans = self.count_scans()
        print(f"\n🔍 SCANNING ACTIVITY:")
        print(f"   Total Scans: {scans}")
        if runtime:
            scans_per_hour = scans / runtime['total_hours'] if runtime['total_hours'] > 0 else 0
            print(f"   Scans per Hour: {scans_per_hour:.1f}")
            print(f"   Expected: 4 scans/hour (every 15 min)")
        
        # Signal analysis
        signals = self.analyze_signals()
        print(f"\n📊 SIGNAL ANALYSIS:")
        print(f"   Total Signals Analyzed: {signals['total_signals_checked']}")
        print(f"   Signal Types:")
        for sig_type, count in signals['signal_types'].items():
            pct = (count / signals['total_signals_checked'] * 100) if signals['total_signals_checked'] > 0 else 0
            print(f"      {sig_type}: {count} ({pct:.1f}%)")
        print(f"   Star Distribution:")
        for stars, count in signals['star_distribution'].items():
            pct = (count / signals['total_signals_checked'] * 100) if signals['total_signals_checked'] > 0 else 0
            print(f"      {'⭐' * stars} {stars} stars: {count} ({pct:.1f}%)")
        
        # Symbol analysis
        print(f"\n📈 PER-SYMBOL ANALYSIS:")
        symbols = self.analyze_symbols()
        for symbol, data in sorted(symbols.items()):
            print(f"   {symbol}:")
            print(f"      Checks: {data['total']}")
            print(f"      Avg Stars: {data['avg_stars']:.2f}")
            print(f"      Max Stars: {data['max_stars']}")
        
        # Trade execution
        trades = self.check_trades_executed()
        print(f"\n💰 TRADE EXECUTION:")
        print(f"   Trades Executed: {trades['trades_executed']}")
        print(f"   Min Stars Required: 3⭐")
        if trades['trades_executed'] == 0:
            print(f"   ⚠️  No trades executed - signals below 3-star threshold")
        
        # Position monitoring
        positions = self.check_positions()
        print(f"\n🎯 POSITION MONITORING:")
        print(f"   Position Checks: {positions['position_checks']}")
        print(f"   Max Concurrent Positions: {positions['max_concurrent']}")
        if positions['position_checks'] > 0:
            print(f"   Avg Open Positions: {positions['avg_positions']:.2f}")
        
        # Error analysis
        errors = self.check_errors()
        print(f"\n⚠️  ERROR & WARNING SUMMARY:")
        print(f"   Errors: {errors['error_count']}")
        print(f"   Warnings: {errors['warning_count']}")
        
        if errors['errors']:
            print(f"\n   Recent Errors:")
            for i, err in enumerate(errors['errors'][:5], 1):
                print(f"      {i}. {err[:100]}...")
        
        if errors['warnings']:
            print(f"\n   Recent Warnings:")
            for i, warn in enumerate(errors['warnings'][:5], 1):
                print(f"      {i}. {warn[:100]}...")
        
        print("\n" + "=" * 80)
        print("📊 KEY OBSERVATIONS:")
        print("=" * 80)
        
        # Generate insights
        if signals['total_signals_checked'] > 0:
            hold_pct = (signals['signal_types'].get('HOLD', 0) / signals['total_signals_checked'] * 100)
            if hold_pct > 90:
                print("   ⚠️  MOSTLY HOLD SIGNALS")
                print("      - Market is ranging or consolidating")
                print("      - Strategy correctly avoiding low-probability trades")
                print("      - This is NORMAL and protects capital")
        
        max_stars = max(signals['star_distribution'].keys()) if signals['star_distribution'] else 0
        if max_stars < 3:
            print("   ⚠️  NO HIGH-CONVICTION SIGNALS FOUND")
            print(f"      - Max signal strength: {max_stars}⭐")
            print("      - Bot requires 3⭐ minimum for execution")
            print("      - Market conditions not favorable for entry")
            print("      - Expected behavior during consolidation periods")
        
        if errors['error_count'] == 0:
            print("   ✅ NO ERRORS - Bot running smoothly")
        
        if connection == 'MAINNET ⚠️ LIVE TRADING':
            print("   ⚠️⚠️⚠️  LIVE TRADING DETECTED")
            print("      - Bot is trading with REAL MONEY")
            print("      - Monitor performance closely")
            print("      - Verify risk settings are correct")
        
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS:")
        print("=" * 80)
        
        if trades['trades_executed'] == 0 and scans > 20:
            print("   1. Monitor for 24-48 hours to collect more data")
            print("   2. Check if market is in consolidation phase")
            print("   3. Consider reducing min_signal_stars to 2 if needed")
            print("   4. Review strategy parameters in MTF analyzer")
            print("   5. Wait for trending market conditions")
        else:
            print("   1. Bot is operating as expected")
            print("   2. Continue monitoring for trade signals")
            print("   3. Review daily reports in Discord")
        
        print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = "server_logs/athena_bot.log"
    
    if not Path(log_file).exists():
        print(f"❌ Log file not found: {log_file}")
        print(f"\nUsage: python analyze_logs.py [log_file_path]")
        print(f"Default: python analyze_logs.py server_logs/athena_bot.log")
        sys.exit(1)
    
    analyzer = LogAnalyzer(log_file)
    analyzer.generate_report()
