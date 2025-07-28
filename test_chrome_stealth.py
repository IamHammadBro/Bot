#!/usr/bin/env python3
"""
Test script to verify Chrome stealth capabilities
"""

import asyncio
import json
from github_premium_bot import PremiumSpotifyBot

async def test_stealth():
    """Test Chrome stealth detection"""
    
    # Test config
    config = {
        'bot_id': 'test',
        'username': 'test@example.com',
        'password': 'testpass',
        'playlist_url': 'https://open.spotify.com/playlist/test',
        'headless': False  # Set to True for headless testing
    }
    
    bot = PremiumSpotifyBot(config)
    
    try:
        print("🧪 Testing Chrome stealth capabilities...")
        
        # Create browser
        context, ai_behavior = await bot.create_premium_browser()
        page = await context.new_page()
        
        print("✅ Browser created successfully!")
        
        # Test detection page
        await page.goto('https://bot.sannysoft.com/')
        await asyncio.sleep(5)  # Let page load
        
        # Check for detection
        user_agent = await page.evaluate('() => navigator.userAgent')
        webdriver = await page.evaluate('() => navigator.webdriver')
        chrome_object = await page.evaluate('() => !!window.chrome')
        plugins_count = await page.evaluate('() => navigator.plugins.length')
        
        print(f"📱 User Agent: {user_agent}")
        print(f"🔍 WebDriver detected: {webdriver}")
        print(f"🌐 Chrome object present: {chrome_object}")
        print(f"🔌 Plugins count: {plugins_count}")
        
        # Check for automation indicators
        cdc_vars = await page.evaluate('''() => {
            const cdcVars = [];
            for (let prop in window) {
                if (prop.includes('cdc_')) {
                    cdcVars.push(prop);
                }
            }
            return cdcVars;
        }''')
        
        print(f"🤖 CDC variables found: {len(cdc_vars)}")
        if cdc_vars:
            print(f"   Variables: {cdc_vars}")
        
        # Wait for user to see results
        print("\n🎯 Check the browser page for detection results...")
        print("💡 Green = Good (not detected), Red = Bad (detected)")
        print("⏱️  Waiting 30 seconds for you to review...")
        
        await asyncio.sleep(30)
        
        await context.close()
        
        # Clean up Chrome process if it exists
        if hasattr(bot, 'chrome_process'):
            try:
                bot.chrome_process.terminate()
                print("🔄 Chrome process terminated")
            except:
                pass
        
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Clean up on error
        if hasattr(bot, 'chrome_process'):
            try:
                bot.chrome_process.terminate()
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_stealth())
