"""
Test script to verify all components are working correctly
Run this before starting the bot to ensure everything is configured properly
"""
import sys
import os

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False

def check_imports():
    """Check if all required packages are installed"""
    print("\n🔍 Checking required packages...")
    packages = {
        'discord': 'discord.py',
        'binance': 'python-binance',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'ta': 'ta',
        'dotenv': 'python-dotenv',
        'colorlog': 'colorlog',
        'aiohttp': 'aiohttp',
    }
    
    all_good = True
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (pip install {package})")
            all_good = False
    
    return all_good

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("      Copy .env.example to .env and configure it")
        return False
    
    print("   ✅ .env file exists")
    
    # Check required variables
    required_vars = [
        'DISCORD_BOT_TOKEN',
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing_vars.append(var)
            print(f"   ⚠️  {var} not configured")
        else:
            print(f"   ✅ {var} configured")
    
    if missing_vars:
        print(f"\n   ❌ Please configure: {', '.join(missing_vars)}")
        return False
    
    return True

def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking directories...")
    
    directories = ['logs', 'trading_data']
    all_good = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            print(f"   ⚠️  {directory}/ (will be created)")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"      Created {directory}/")
            except Exception as e:
                print(f"      ❌ Failed to create {directory}/: {e}")
                all_good = False
    
    return all_good

def check_config():
    """Check if config.py can be imported"""
    print("\n🔍 Checking configuration...")
    
    try:
        import config
        print("   ✅ config.py loaded")
        
        # Check critical config values
        if hasattr(config, 'DISCORD_BOT_TOKEN'):
            print("   ✅ Discord configuration loaded")
        if hasattr(config, 'BINANCE_API_KEY'):
            print("   ✅ Binance configuration loaded")
        if hasattr(config, 'AVAILABLE_STRATEGIES'):
            print(f"   ✅ {len(config.AVAILABLE_STRATEGIES)} strategies available")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to load config: {e}")
        return False

def check_bot_files():
    """Check if all bot files exist"""
    print("\n🔍 Checking bot files...")
    
    required_files = [
        'bot.py',
        'binance_client.py',
        'signal_analyzer.py',
        'strategies.py',
        'config.py',
        'logger.py'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
            all_good = False
    
    return all_good

def test_binance_connection():
    """Test connection to Binance"""
    print("\n🔍 Testing Binance connection...")
    
    try:
        from binance_client import BinanceFuturesClient
        import config
        
        client = BinanceFuturesClient(
            config.BINANCE_API_KEY,
            config.BINANCE_API_SECRET,
            config.BINANCE_TESTNET
        )
        
        # Try to get account balance
        balance = client.get_account_balance()
        
        if balance or balance == {}:
            print("   ✅ Connected to Binance successfully")
            if config.BINANCE_TESTNET:
                print("   ℹ️  Using TESTNET")
            else:
                print("   ℹ️  Using MAINNET")
            return True
        else:
            print("   ⚠️  Connected but no balance data")
            return True
            
    except Exception as e:
        print(f"   ❌ Binance connection failed: {e}")
        print("      Check your API keys and permissions")
        return False

def main():
    """Run all checks"""
    print("=" * 50)
    print("🤖 Athena Trading Bot - System Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_imports),
        ("Environment File", check_env_file),
        ("Directories", check_directories),
        ("Bot Files", check_bot_files),
        ("Configuration", check_config),
        ("Binance Connection", test_binance_connection),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n   ❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to run the bot.")
        print("\n   Start the bot with:")
        print("   python bot.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("   See README.md for detailed setup instructions.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
