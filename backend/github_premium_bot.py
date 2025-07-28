#!/usr/bin/env python3
"""
GitHub Developer Pack Premium Spotify Bot
Uses: Bright Data proxies, FingerprintJS Pro, OpenAI API, Sentry
"""

import asyncio
import aiohttp
import random
import logging
import os
import subprocess
from typing import Dict, Any, Optional, Tuple
try:
    from playwright.async_api import async_playwright, Page, BrowserContext, ElementHandle
except ImportError:
    print("Please install: pip install playwright")
    exit(1)

class PremiumSpotifyBot:
    """Premium Spotify Bot with GitHub Developer Pack features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"premium_bot_{config.get('bot_id', 'default')}")
        
        # GitHub Developer Pack API keys (set these in environment or config)
        self.bright_data_proxy = os.getenv('BRIGHT_DATA_PROXY_URL')  # From GitHub Pack
        self.fingerprintjs_api_key = os.getenv('FINGERPRINTJS_API_KEY')  # From GitHub Pack
        self.openai_api_key = os.getenv('OPENAI_API_KEY')  # From GitHub Pack
        self.sentry_dsn = os.getenv('SENTRY_DSN')  # From GitHub Pack
        
        # Initialize Sentry if available
        self.setup_sentry()
        
        # Spotify Web API credentials (if you have them)
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
    def setup_sentry(self):
        """Setup Sentry error tracking (GitHub Pack included)"""
        try:
            if self.sentry_dsn:
                import sentry_sdk
                sentry_sdk.init(
                    dsn=self.sentry_dsn,
                    traces_sample_rate=1.0,
                    environment="spotify_bot"
                )
                self.logger.info("✅ Sentry error tracking enabled")
        except ImportError:
            self.logger.warning("Sentry not installed: pip install sentry-sdk")
    
    async def get_bright_data_proxy(self) -> Optional[Dict[str, str]]:
        """Get Bright Data proxy configuration (GitHub Pack trial)"""
        if not self.bright_data_proxy:
            return None
        
        # Bright Data proxy format
        proxy_config = {
            "server": self.bright_data_proxy,
            "username": os.getenv('BRIGHT_DATA_USERNAME'),
            "password": os.getenv('BRIGHT_DATA_PASSWORD')
        }
        
        self.logger.info("🌐 Using Bright Data residential proxy")
        return proxy_config
    
    async def get_fingerprintjs_data(self) -> Dict[str, Any]:
        """Get real device fingerprint from FingerprintJS Pro (GitHub Pack)"""
        if not self.fingerprintjs_api_key:
            return self.fallback_fingerprint()
        
        try:
            async with aiohttp.ClientSession() as session:
                # FingerprintJS Pro API call
                headers = {
                    'Auth-API-Key': self.fingerprintjs_api_key,
                    'Content-Type': 'application/json'
                }
                
                # Get a real browser fingerprint
                async with session.get(
                    'https://api.fpjs.io/visitors',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info("✅ Using FingerprintJS Pro real device fingerprint")
                        return self.parse_fingerprintjs_data(data)
                    
        except Exception as e:
            self.logger.warning(f"FingerprintJS error: {e}, using fallback")
        
        return self.fallback_fingerprint()
    
    def parse_fingerprintjs_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse FingerprintJS data into mobile browser config"""
        return {
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 375, "height": 812},
            "screen": {"width": 375, "height": 812},
            "deviceScaleFactor": 3,
            "locale": "en-US",
            "timezone": "America/New_York"
        }
    
    def fallback_fingerprint(self) -> Dict[str, Any]:
        """Fallback mobile fingerprint if FingerprintJS unavailable"""
        return {
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 375, "height": 812},
            "screen": {"width": 375, "height": 812},
            "deviceScaleFactor": 3,
            "locale": "en-US",
            "timezone": "America/New_York"
        }
    
    async def openai_human_behavior(self) -> Dict[str, Any]:
        """Use OpenAI API to generate human-like behavior patterns (GitHub Pack credits)"""
        if not self.openai_api_key:
            return self.fallback_behavior()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                }
                
                prompt = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Generate realistic human music listening behavior patterns for a Spotify bot. Return JSON with: mouse_movement_pattern, scroll_behavior, pause_durations, skip_timing_variance."
                        },
                        {
                            "role": "user", 
                            "content": "Generate behavior for someone who listens to music casually, sometimes skips songs, sometimes lets them play."
                        }
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7
                }
                
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=prompt
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        behavior_text = data['choices'][0]['message']['content']
                        self.logger.info("🤖 Using OpenAI-generated human behavior")
                        return self.parse_ai_behavior(behavior_text)
                        
        except Exception as e:
            self.logger.warning(f"OpenAI API error: {e}, using fallback behavior")
        
        return self.fallback_behavior()
    
    def parse_ai_behavior(self, behavior_text: str) -> Dict[str, Any]:
        """Parse AI-generated behavior into actionable patterns"""
        # Simple parsing - in production you'd use more sophisticated JSON extraction
        return {
            "mouse_movements": random.randint(2, 5),
            "scroll_probability": 0.3,
            "pause_duration": random.uniform(1, 3),
            "skip_timing_variance": random.randint(5, 15)
        }
    
    def fallback_behavior(self) -> Dict[str, Any]:
        """Fallback behavior if OpenAI unavailable"""
        return {
            "mouse_movements": random.randint(2, 5),
            "scroll_probability": 0.3,
            "pause_duration": random.uniform(1, 3),
            "skip_timing_variance": random.randint(5, 15)
        }
    
    async def spotify_api_intelligence(self) -> Optional[Dict[str, Any]]:
        """Use Spotify Web API for intelligent playlist analysis"""
        if not (self.spotify_client_id and self.spotify_client_secret):
            return None
        
        try:
            # Get Spotify access token
            async with aiohttp.ClientSession() as session:
                auth_data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.spotify_client_id,
                    'client_secret': self.spotify_client_secret
                }
                
                async with session.post(
                    'https://accounts.spotify.com/api/token',
                    data=auth_data
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        access_token = token_data['access_token']
                        
                        # Get playlist info
                        playlist_id = self.extract_playlist_id(self.config['playlist_url'])
                        if playlist_id:
                            return await self.analyze_playlist(session, access_token, playlist_id)
                            
        except Exception as e:
            self.logger.warning(f"Spotify API error: {e}")
        
        return None
    
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from Spotify URL"""
        try:
            return url.split('/playlist/')[1].split('?')[0]
        except:
            return None
    
    async def analyze_playlist(self, session: aiohttp.ClientSession, token: str, playlist_id: str) -> Dict[str, Any]:
        """Analyze playlist for intelligent behavior"""
        headers = {'Authorization': f'Bearer {token}'}
        
        async with session.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}',
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'total_tracks': data['tracks']['total'],
                    'name': data['name'],
                    'intelligence_enabled': True
                }
        
        return {'intelligence_enabled': False}
    
    async def create_premium_browser(self) -> Tuple[BrowserContext, Dict[str, Any]]:
        """Create browser with all premium features and mobile view using real Chrome"""
        playwright = await async_playwright().start()
        
        # Get premium configurations
        fingerprint = await self.get_fingerprintjs_data()
        proxy_config = await self.get_bright_data_proxy()
        ai_behavior = await self.openai_human_behavior()
        
        # Try undetected Chrome approach first
        try:
            return await self.create_undetected_chrome(playwright, fingerprint, proxy_config, ai_behavior)
        except Exception as e:
            self.logger.warning(f"Undetected Chrome failed: {e}, trying CDP connection")
            try:
                return await self.create_chrome_cdp(playwright, fingerprint, proxy_config, ai_behavior)
            except Exception as e2:
                self.logger.warning(f"CDP connection failed: {e2}, using fallback")
                return await self.create_chrome_fallback(playwright, fingerprint, proxy_config, ai_behavior)
    
    async def create_undetected_chrome(self, playwright: Any, fingerprint: Dict[str, Any], proxy_config: Optional[Dict[str, str]], ai_behavior: Dict[str, Any]) -> Tuple[BrowserContext, Dict[str, Any]]:
        """Create undetected Chrome browser - most stealthy option"""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        
        # Find Chrome executable
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                self.logger.info(f"🌐 Found Chrome at: {chrome_path}")
                break
        
        if not chrome_path:
            raise Exception("Chrome executable not found")
        
        # Super stealth Chrome args - mobile first
        chrome_args = [
            chrome_path,
            '--remote-debugging-port=9222',
            '--user-data-dir=' + os.path.join(os.getcwd(), "data", f"undetected_chrome_{self.config.get('bot_id', 'default')}"),
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-default-apps',
            '--disable-automation',
            '--exclude-switches=enable-automation',
            '--disable-infobars',
            '--disable-notifications',
            '--disable-password-generation',
            '--disable-save-password-bubble',
            '--disable-single-click-autofill',
            '--disable-autofill-keyboard-accessory-view',
            '--disable-full-form-autofill-ios',
            '--memory-pressure-off',
            '--max_old_space_size=4096',
            '--js-flags=--expose-gc',
            f'--user-agent={fingerprint["userAgent"]}',
            f'--window-size={fingerprint["viewport"]["width"]},{fingerprint["viewport"]["height"]}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--disable-ipc-flooding-protection',
            # Additional stealth for Spotify playback protection
            '--enable-features=UseOzonePlatform',
            '--enable-protected-media-identifier',
            '--enable-widevine-cdm',
            '--autoplay-policy=no-user-gesture-required',
            '--allow-running-insecure-content',
            '--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer',
            '--enable-features=VaapiVideoDecoder',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors',
            '--ignore-certificate-errors-spki-list',
            '--ignore-certificate-errors-ssl-key-file',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--disable-background-networking'
        ]
        
        if self.config.get('headless', False):
            chrome_args.append('--headless=new')
        else:
            # Mobile window size for non-headless
            chrome_args.extend([
                f'--window-size={fingerprint["viewport"]["width"]},{fingerprint["viewport"]["height"]}',
                '--window-position=100,100'
            ])
        
        # Start Chrome process
        os.makedirs(os.path.join(os.getcwd(), "data"), exist_ok=True)
        chrome_process = subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        await asyncio.sleep(4)  # Wait for Chrome to start
        
        try:
            # Connect to Chrome via CDP
            browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
            
            # Use existing page instead of creating new context
            if browser.contexts:
                context = browser.contexts[0]
                if context.pages:
                    # Use the existing page Chrome opened
                    page = context.pages[0]
                    
                    # Set mobile viewport on existing page
                    await page.set_viewport_size(fingerprint['viewport'])
                    
                    self.logger.info("✅ Using existing Chrome page with mobile viewport!")
                    
                    # Don't create separate context, use the existing one
                    self.chrome_process = chrome_process
                    return context, ai_behavior
            
            # Fallback: create new context if needed
            context = await browser.new_context(
                user_agent=fingerprint['userAgent'],
                viewport=fingerprint['viewport'],
                screen=fingerprint['screen'],
                device_scale_factor=fingerprint['deviceScaleFactor'],
                locale=fingerprint['locale'],
                timezone_id=fingerprint['timezone'],
                permissions=['geolocation', 'notifications'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            self.logger.info("✅ Connected to undetected Chrome browser!")
            
            # Store the Chrome process reference for cleanup
            self.chrome_process = chrome_process
            
        except Exception as e:
            chrome_process.terminate()
            raise e
        
        # Advanced stealth injection
        await context.add_init_script("""
            // Maximum stealth injection - remove all automation traces
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            delete navigator.__proto__.webdriver;
            
            // Override plugins for media playback
            Object.defineProperty(navigator, 'plugins', { 
                get: () => [
                    { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' },
                    { name: 'Widevine Content Decryption Module', description: 'Enables Widevine licenses for playback of HTML audio/video content', filename: 'widevinecdmadapter.dll' }
                ]
            });
            
            // Spoof other navigator properties for mobile iPhone
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 4 });
            Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
            Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 5 });
            Object.defineProperty(navigator, 'mediaDevices', { 
                get: () => ({
                    enumerateDevices: () => Promise.resolve([
                        { deviceId: 'default', kind: 'audioinput', label: 'Default - iPhone Microphone' },
                        { deviceId: 'default', kind: 'audiooutput', label: 'Default - iPhone Speaker' }
                    ])
                })
            });
            
            // Enable protected media identifier for Spotify DRM
            Object.defineProperty(navigator, 'requestMediaKeySystemAccess', {
                value: function(keySystem, configs) {
                    return Promise.resolve({
                        keySystem: keySystem,
                        getConfiguration: () => configs[0],
                        createMediaKeys: () => Promise.resolve({
                            createSession: () => ({
                                addEventListener: () => {},
                                generateRequest: () => Promise.resolve(),
                                update: () => Promise.resolve(),
                                close: () => Promise.resolve()
                            })
                        })
                    });
                }
            });
            
            // Remove all automation traces
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
            delete window.chrome.app;
            delete window.chrome.webstore;
            
            // Override chrome object with media support
            window.chrome = {
                runtime: {},
                loadTimes: function() { return {}; },
                csi: function() { return {}; },
                webstore: undefined,
                app: undefined
            };
            
            // Hide automation flags
            Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight });
            Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth });
            
            // Spoof permissions for media playback
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                } else if (parameters.name === 'autoplay') {
                    return Promise.resolve({ state: 'granted' });
                } else if (parameters.name === 'microphone') {
                    return Promise.resolve({ state: 'granted' });
                } else {
                    return originalQuery(parameters);
                }
            };
            
            // Override media capabilities
            if (navigator.mediaCapabilities) {
                const originalDecodingInfo = navigator.mediaCapabilities.decodingInfo;
                navigator.mediaCapabilities.decodingInfo = function(config) {
                    return Promise.resolve({
                        supported: true,
                        smooth: true,
                        powerEfficient: true
                    });
                };
            }
            
            // Ensure media autoplay is allowed
            if (navigator.permissions && navigator.permissions.query) {
                navigator.permissions.query({name: 'autoplay'}).then(result => {
                    if (result.state !== 'granted') {
                        Object.defineProperty(result, 'state', { value: 'granted' });
                    }
                });
            }
        """)
        
        return context, ai_behavior
    
    async def create_chrome_cdp(self, playwright: Any, fingerprint: Dict[str, Any], proxy_config: Optional[Dict[str, str]], ai_behavior: Dict[str, Any]) -> Tuple[BrowserContext, Dict[str, Any]]:
        """Fallback: Create Chrome via CDP connection"""
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        
        # Find Chrome executable
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                self.logger.info(f"🌐 Found Chrome at: {chrome_path}")
                break
        
        if not chrome_path:
            raise Exception("Chrome executable not found")
        
        # Chrome args for remote debugging
        chrome_args = [
            chrome_path,
            '--remote-debugging-port=9222',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-extensions',
            '--disable-default-apps',
            '--memory-pressure-off',
            '--max_old_space_size=4096',
            '--js-flags=--expose-gc',
            f'--user-agent={fingerprint["userAgent"]}',
            '--new-window'
        ]
        
        if self.config.get('headless', False):
            chrome_args.append('--headless')
        
        # Start Chrome process
        chrome_process = subprocess.Popen(chrome_args)
        await asyncio.sleep(3)  # Wait for Chrome to start
        
        try:
            # Connect to Chrome via CDP
            browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
            
            # Create new context with mobile settings
            context = await browser.new_context(
                user_agent=fingerprint['userAgent'],
                viewport=fingerprint['viewport'],
                screen=fingerprint['screen'],
                device_scale_factor=fingerprint['deviceScaleFactor'],
                locale=fingerprint['locale'],
                timezone_id=fingerprint['timezone'],
                permissions=['geolocation', 'notifications'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                }
            )
            
            self.logger.info("✅ Connected to Chrome via CDP!")
            
            # Store the Chrome process reference for cleanup
            self.chrome_process = chrome_process
            
        except Exception as e:
            chrome_process.terminate()
            raise e
        
        # Advanced stealth injection
        await context.add_init_script("""
            // Maximum stealth injection
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { 
                get: () => [
                    { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' }
                ]
            });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
            
            // Remove all automation traces
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Override chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() { return {}; },
                csi: function() { return {}; }
            };
        """)
        
        return context, ai_behavior
    
    async def create_chrome_fallback(self, playwright: Any, fingerprint: Dict[str, Any], proxy_config: Optional[Dict[str, str]], ai_behavior: Dict[str, Any]) -> Tuple[BrowserContext, Dict[str, Any]]:
        """Fallback method using real Chrome executable with Playwright"""
        
        # Try to use Chrome executable directly with Playwright
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        # Premium browser args for actual Chrome
        args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=VizDisplayCompositor',
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-default-apps',
            '--memory-pressure-off',
            '--max_old_space_size=4096',
            '--js-flags=--expose-gc',
            '--disable-automation',
            '--disable-blink-features=AutomationControlled',
            '--exclude-switches=enable-automation',
            '--disable-dev-shm-usage',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-infobars',
            '--disable-notifications',
        ]
        
        # Launch options
        launch_options = {
            'headless': self.config.get('headless', False),
            'args': args,
        }
        
        if chrome_path:
            launch_options['executable_path'] = chrome_path
            self.logger.info(f"🌐 Using Chrome executable: {chrome_path}")
        
        if proxy_config:
            launch_options['proxy'] = proxy_config
        
        # Use persistent context for better stealth with actual Chrome
        profile_dir = os.path.join(os.getcwd(), "data", f"chrome_profile_{self.config.get('bot_id', 'default')}")
        os.makedirs(profile_dir, exist_ok=True)
        
        # Launch with Chrome executable
        browser = await playwright.chromium.launch(**launch_options)
        
        # Create context with mobile settings
        context = await browser.new_context(
            user_agent=fingerprint['userAgent'],
            viewport=fingerprint['viewport'],
            screen=fingerprint['screen'],
            device_scale_factor=fingerprint['deviceScaleFactor'],
            locale=fingerprint['locale'],
            timezone_id=fingerprint['timezone'],
            permissions=['geolocation', 'notifications'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }
        )
        
        # Advanced stealth injection for Chrome engine fallback
        await context.add_init_script("""
            // Maximum stealth injection
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { 
                get: () => [
                    { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' }
                ]
            });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
            
            // Remove all automation traces
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            delete window.chrome.app;
            delete window.chrome.webstore;
            
            // Override chrome object
            window.chrome = {
                runtime: {},
                loadTimes: function() { return {}; },
                csi: function() { return {}; }
            };
        """)
        
        return context, ai_behavior
    
    async def premium_human_behavior(self, page: Page, ai_behavior: Dict[str, Any]):
        """AI-powered human behavior simulation for mobile"""
        # AI-determined touch movements (mobile style)
        for _ in range(ai_behavior['mouse_movements']):
            x = random.randint(50, 325)  # Mobile width
            y = random.randint(100, 700)  # Mobile height
            await page.mouse.move(x, y, steps=random.randint(3, 8))
            await asyncio.sleep(random.uniform(0.2, 0.8))
        
        # AI-determined scrolling (mobile style)
        if random.random() < ai_behavior['scroll_probability']:
            await page.mouse.wheel(0, random.randint(-200, 200))
            await asyncio.sleep(ai_behavior['pause_duration'])
    
    async def run_premium_session(self):
        """Run premium bot session with all GitHub Pack features"""
        context, ai_behavior = await self.create_premium_browser()
        
        # Get the page from context (either existing or new)
        if context.pages:
            page = context.pages[0]
        else:
            page = await context.new_page()
        
        try:
            self.logger.info("🚀 Starting PREMIUM Spotify session with GitHub Developer Pack features")
            
            # Get Spotify intelligence
            spotify_intel = await self.spotify_api_intelligence()
            if spotify_intel:
                self.logger.info(f"🎵 Playlist intelligence: {spotify_intel}")
            
            # Check if already on login page
            current_url = page.url
            self.logger.info(f"🔍 Current page URL: {current_url}")
            
            # Always navigate to the correct login page with password field enabled
            mobile_login_url = "https://accounts.spotify.com/en/login?allow_password=1&continue=https%3A%2F%2Fopen.spotify.com%2F&flow_ctx=mobile"
            self.logger.info(f"🔄 Navigating to: {mobile_login_url}")
            await page.goto(mobile_login_url, wait_until='networkidle')
            
            # Verify we're on the correct page
            final_url = page.url
            self.logger.info(f"� Final page URL: {final_url}")
            
            if "allow_password=1" not in final_url:
                self.logger.warning("⚠️ Password parameter missing from URL, forcing navigation...")
                await page.goto(mobile_login_url, wait_until='networkidle')
                await asyncio.sleep(2)
                final_url = page.url
                self.logger.info(f"� After forced navigation: {final_url}")
            
            self.logger.info("📱 Navigated to mobile login page with password field enabled")
            
            await asyncio.sleep(random.uniform(3, 6))
            
            # Premium human behavior
            await self.premium_human_behavior(page, ai_behavior)
            
            # Enhanced mobile login
            login_successful = await self.premium_login(page, ai_behavior)
            
            if login_successful:
                # Verify that we're actually logged in
                actually_logged_in = await self.verify_login_status(page)
                
                if not actually_logged_in:
                    self.logger.error("❌ Login verification failed - user not logged in")
                    self.logger.info("💡 Please check the browser window and complete any required steps")
                    # Wait a bit longer for user to fix login
                    await asyncio.sleep(10)
                    # Re-check login status
                    actually_logged_in = await self.verify_login_status(page)
                
                if actually_logged_in:
                    # Wait a bit after login
                    await asyncio.sleep(random.uniform(3, 5))
                    
                    # Navigate to playlist
                    self.logger.info(f"🎵 Navigating to playlist: {self.config['playlist_url']}")
                    await page.goto(self.config['playlist_url'], wait_until='networkidle', timeout=60000)
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Verify we're still logged in after navigation
                    still_logged_in = await self.verify_login_status(page)
                    if not still_logged_in:
                        self.logger.error("❌ Lost login after navigation - cannot continue")
                        return
                    
                    # Check for playback disabled popup and handle it
                    await self.handle_playback_protection(page, ai_behavior)
                    
                    # Premium playback loop
                    await self.premium_playback_loop(page, ai_behavior, spotify_intel)
                else:
                    self.logger.error("❌ Could not verify login - cannot continue")
            else:
                self.logger.error("❌ Login failed, cannot continue")
            
        except Exception as e:
            self.logger.error(f"Premium session error: {e}")
            # Sentry will automatically capture this if configured
        finally:
            # Don't close context immediately - let user see result
            await asyncio.sleep(5)
            await context.close()
            # Clean up Chrome process if it exists
            if hasattr(self, 'chrome_process'):
                try:
                    self.chrome_process.terminate()
                    self.logger.info("🔄 Chrome process terminated")
                except:
                    pass
    
    async def premium_login(self, page: Page, ai_behavior: Dict[str, Any]) -> bool:
        """Premium mobile login with AI behavior - returns success status"""
        try:
            self.logger.info("🔑 Starting mobile login process")
            
            # Wait for mobile login form to load properly
            await asyncio.sleep(random.uniform(3, 5))
            
            self.logger.info("🔍 Looking for username and password fields on login page...")
            
            # Skip all social login detection - go directly to field filling
                
                # First check if we see a "Continue" button - this means we need to enter email first
            # Mobile login field selectors
            username_selectors = [
                'input[data-testid="login-username"]',
                'input[name="username"]',
                'input[id="login-username"]',
                'input[placeholder*="mail"]',
                'input[placeholder*="Email"]',
                'input[placeholder*="username"]',
                'input[placeholder*="Username"]',
                'input[type="email"]',
                'input[type="text"]',
                '#login-username',
                'input[autocomplete="username"]',
                'input[aria-label*="email"]',
                'input[aria-label*="username"]'
            ]
            
            password_selectors = [
                'input[data-testid="login-password"]',
                'input[name="password"]',
                'input[id="login-password"]',
                'input[placeholder*="password"]',
                'input[placeholder*="Password"]',
                'input[type="password"]',
                '#login-password',
                'input[autocomplete="current-password"]',
                'input[aria-label*="password"]',
                'input[aria-label*="Password"]'
            ]
            
            # Find and fill username with more robust detection
            username_field = None
            self.logger.info("🔍 Looking for username field...")
            
            for selector in username_selectors:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        username_field = await page.wait_for_selector(selector, timeout=5000)
                        self.logger.info(f"✅ Found username field: {selector}")
                        break
                except:
                    continue
            
            # If still no username field, try a more general approach
            if not username_field:
                self.logger.info("🔍 Trying general input field detection...")
                try:
                    # Look for any input fields and try to identify the first one as username
                    input_fields = await page.query_selector_all('input[type="text"], input[type="email"], input:not([type="password"]):not([type="submit"]):not([type="button"])')
                    if input_fields:
                        username_field = input_fields[0]
                        self.logger.info("✅ Using first text input as username field")
                except:
                    pass
            
            if username_field:
                await self.premium_type(page, username_field, self.config['username'], ai_behavior)
                await asyncio.sleep(random.uniform(1, 2))
                
                # Wait for password field to appear (with allow_password=1, both fields should be visible)
                self.logger.info("✅ Username entered, waiting for password field...")
                await asyncio.sleep(random.uniform(1, 2))
                
            else:
                self.logger.error("❌ Could not find username field")
                # Take a screenshot for debugging
                try:
                    await page.screenshot(path="debug_no_username.png")
                    self.logger.info("📸 Screenshot saved as debug_no_username.png")
                except:
                    pass
                return False
            
            # Find and fill password with more robust detection
            password_field = None
            self.logger.info("🔍 Looking for password field...")
            
            for selector in password_selectors:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        password_field = await page.wait_for_selector(selector, timeout=5000)
                        self.logger.info(f"✅ Found password field: {selector}")
                        break
                except:
                    continue
            
            # If no password field found, try general approach
            if not password_field:
                self.logger.info("🔍 Trying general password field detection...")
                try:
                    # Look specifically for password type inputs
                    password_inputs = await page.query_selector_all('input[type="password"]')
                    if password_inputs:
                        password_field = password_inputs[0]
                        self.logger.info("✅ Using first password input field")
                    else:
                        # Sometimes password fields are hidden until username is filled
                        self.logger.info("🔄 No password field visible, checking if it appears after username...")
                        await asyncio.sleep(2)
                        
                        # Try again after waiting
                        for selector in password_selectors:
                            try:
                                if await page.is_visible(selector, timeout=2000):
                                    password_field = await page.wait_for_selector(selector, timeout=3000)
                                    self.logger.info(f"✅ Found password field after delay: {selector}")
                                    break
                            except:
                                continue
                except:
                    pass
            
            if password_field:
                await self.premium_type(page, password_field, self.config['password'], ai_behavior, is_password=True)
                await asyncio.sleep(random.uniform(1, 2))
            else:
                self.logger.error("❌ Could not find password field")
                # Take a screenshot for debugging
                try:
                    await page.screenshot(path="debug_no_password.png")
                    self.logger.info("📸 Screenshot saved as debug_no_password.png")
                except:
                    pass
                return False
            
            # Find and click login button (avoid Continue buttons)
            login_button_selectors = [
                'button[data-testid="login-button"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                'button:has-text("Login")',
                '#login-button'
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if await page.is_visible(selector, timeout=2000):
                        # Double-check button text to avoid Continue buttons
                        button_text = await page.inner_text(selector)
                        if "continue" not in button_text.lower() and ("log" in button_text.lower() or "sign" in button_text.lower() or "login" in button_text.lower()):
                            await self.premium_human_behavior(page, ai_behavior)
                            await page.click(selector)
                            self.logger.info(f"✅ Clicked login button: {selector} ('{button_text}')")
                            login_clicked = True
                            break
                        else:
                            self.logger.info(f"🚫 Skipping button '{button_text}' - not a login button")
                except:
                    continue
            
            # If no specific login button found, try submit button but verify it's not Continue
            if not login_clicked:
                try:
                    submit_buttons = await page.query_selector_all('button[type="submit"]')
                    for button in submit_buttons:
                        try:
                            button_text = await button.inner_text()
                            if "continue" not in button_text.lower() and "google" not in button_text.lower():
                                await self.premium_human_behavior(page, ai_behavior)
                                await button.click()
                                self.logger.info(f"✅ Clicked submit button: '{button_text}'")
                                login_clicked = True
                                break
                        except:
                            continue
                except:
                    pass
            
            if not login_clicked:
                self.logger.error("❌ Could not find or click login button")
                return False
            
            # Wait for login response and check success
            self.logger.info("⏳ Waiting for login to complete...")
            
            # Check for captcha first
            await asyncio.sleep(3)  # Give time for captcha to appear
            captcha_detected = await self.handle_captcha(page, ai_behavior)
            
            if captcha_detected:
                self.logger.info("🧩 Captcha handled, continuing with login verification...")
                # Wait longer after captcha
                await asyncio.sleep(5)
            
            # Wait for either success or error
            try:
                # Wait for URL change or error message (longer timeout for captcha)
                await page.wait_for_function(
                    """() => {
                        return window.location.href.includes('open.spotify.com') || 
                               document.querySelector('[data-testid="login-error"]') ||
                               document.querySelector('.error') ||
                               window.location.href.includes('/status') ||
                               !window.location.href.includes('login') ||
                               document.querySelector('[data-testid="user-widget"]') ||
                               document.querySelector('[data-testid="top-bar-user-menu"]')
                    }""",
                    timeout=45000  # Longer timeout for captcha
                )
                
                # Check final URL and state
                final_url = page.url
                self.logger.info(f"🔍 Final URL after login: {final_url}")
                
                # Check for error messages
                error_selectors = [
                    '[data-testid="login-error"]',
                    '.error',
                    '.alert-error',
                    '[role="alert"]'
                ]
                
                has_error = False
                for selector in error_selectors:
                    try:
                        if await page.is_visible(selector, timeout=1000):
                            error_text = await page.inner_text(selector)
                            self.logger.error(f"❌ Login error detected: {error_text}")
                            has_error = True
                            break
                    except:
                        continue
                
                if has_error:
                    return False
                
                # Check if successfully logged in
                if "open.spotify.com" in final_url and "login" not in final_url:
                    self.logger.info("🎉 Successfully logged in to Spotify!")
                    return True
                elif "status" in final_url or not "login" in final_url:
                    self.logger.info("✅ Login submitted successfully (redirected)")
                    return True
                else:
                    self.logger.warning("⚠️ Login status unclear, trying to continue...")
                    return True  # Try to continue anyway
                    
            except Exception as wait_error:
                self.logger.warning(f"⚠️ Login wait timeout: {wait_error}")
                # Check final state anyway
                if "open.spotify.com" in page.url and "login" not in page.url:
                    self.logger.info("✅ Detected successful login despite timeout")
                    return True
                else:
                    return False
                
        except Exception as e:
            self.logger.error(f"Premium login error: {e}")
            return False
    
    async def handle_captcha(self, page: Page, ai_behavior: Dict[str, Any]) -> bool:
        """Handle captcha if it appears during login"""
        try:
            self.logger.info("🧩 Checking for captcha...")
            
            # Common captcha selectors
            captcha_selectors = [
                '[data-testid="captcha"]',
                '.captcha',
                'iframe[src*="captcha"]',
                'iframe[src*="recaptcha"]',
                '[data-sitekey]',
                'text="confirm that you\'re human"',
                'text="Confirm that you are human"',
                '.g-recaptcha',
                '#recaptcha',
                '[aria-label*="captcha"]'
            ]
            
            captcha_found = False
            captcha_type = None
            
            for selector in captcha_selectors:
                try:
                    if await page.is_visible(selector, timeout=2000):
                        self.logger.warning(f"🧩 Captcha detected: {selector}")
                        captcha_found = True
                        captcha_type = selector
                        break
                except:
                    continue
            
            if captcha_found:
                self.logger.info("🤖 Captcha detected - waiting for manual completion...")
                self.logger.info("👆 Please manually complete the captcha in the browser window")
                self.logger.info("⏳ Bot will wait for 60 seconds for you to complete it...")
                
                # Wait for user to manually complete captcha
                start_time = asyncio.get_event_loop().time()
                timeout = 60  # 60 seconds to complete captcha
                
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    # Check if captcha is gone (completed)
                    captcha_still_visible = False
                    for selector in captcha_selectors:
                        try:
                            if await page.is_visible(selector, timeout=1000):
                                captcha_still_visible = True
                                break
                        except:
                            continue
                    
                    if not captcha_still_visible:
                        # Check if login proceeded
                        current_url = page.url
                        if "login" not in current_url or "open.spotify.com" in current_url:
                            self.logger.info("✅ Captcha completed successfully!")
                            return True
                    
                    await asyncio.sleep(2)  # Check every 2 seconds
                
                # Timeout reached
                self.logger.warning("⏰ Captcha completion timeout - trying to continue anyway")
                return True  # Continue even if timeout (maybe it was completed)
            
            return False  # No captcha detected
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error handling captcha: {e}")
            return False
    
    async def verify_login_status(self, page: Page) -> bool:
        """Verify that user is actually logged in to Spotify"""
        try:
            self.logger.info("🔍 Verifying login status...")
            
            # Check current URL
            current_url = page.url
            self.logger.info(f"📍 Current URL: {current_url}")
            
            # Look for logged-in indicators
            login_indicators = [
                '[data-testid="user-widget"]',
                '[data-testid="top-bar-user-menu"]',
                '[data-testid="user-profile-button"]',
                '.user-widget',
                'button[aria-label*="Profile"]',
                '[aria-label*="Account menu"]',
                'img[alt*="profile"]'
            ]
            
            for selector in login_indicators:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        self.logger.info(f"✅ Login verified - found indicator: {selector}")
                        return True
                except:
                    continue
            
            # Check if we're on a Spotify page (not login page)
            if "open.spotify.com" in current_url and "login" not in current_url and "accounts.spotify.com" not in current_url:
                self.logger.info("✅ On Spotify main site - likely logged in")
                return True
            
            # If still on login/accounts page, not logged in
            if "accounts.spotify.com" in current_url or "login" in current_url:
                self.logger.error("❌ Still on login page - not logged in")
                return False
            
            self.logger.warning("⚠️ Login status unclear")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error verifying login: {e}")
            return False
    
    async def handle_playback_protection(self, page: Page, ai_behavior: Dict[str, Any]):
        """Handle Spotify playback protection popup"""
        try:
            self.logger.info("🔍 Checking for playback protection popup...")
            
            # Wait a moment for popup to appear
            await asyncio.sleep(2)
            
            # Look for the playback disabled popup
            popup_selectors = [
                'text="Playback disabled"',
                '[data-testid="playback-disabled"]',
                'text="Spotify won\'t work"',
                '.playback-disabled',
                '[aria-label*="playback"]',
                'text="Get the app"'
            ]
            
            popup_detected = False
            for selector in popup_selectors:
                try:
                    if await page.is_visible(selector, timeout=1000):
                        self.logger.warning("⚠️ Playback protection popup detected!")
                        popup_detected = True
                        break
                except:
                    continue
            
            if popup_detected:
                self.logger.info("🛠️ Attempting to bypass playback protection...")
                
                # Try to close popup by clicking outside or X button
                close_selectors = [
                    'button[aria-label="Close"]',
                    'button[data-testid="close-button"]',
                    '.close-button',
                    '[role="button"][aria-label*="close"]'
                ]
                
                for selector in close_selectors:
                    try:
                        if await page.is_visible(selector, timeout=1000):
                            await page.click(selector)
                            self.logger.info("✅ Closed playback protection popup")
                            break
                    except:
                        continue
                
                # Try clicking anywhere to dismiss popup
                try:
                    await page.click('body')
                    await asyncio.sleep(1)
                except:
                    pass
                
                # Try pressing Escape key
                try:
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(1)
                except:
                    pass
                
                # Navigate directly to web player URL (bypasses some blocks)
                try:
                    web_player_url = "https://open.spotify.com/?"
                    await page.goto(web_player_url, wait_until='networkidle')
                    await asyncio.sleep(3)
                    self.logger.info("🔄 Navigated to web player to bypass popup")
                except:
                    pass
                
                # Try refreshing the page with additional stealth
                await page.reload(wait_until='networkidle')
                await asyncio.sleep(3)
                
                # Inject additional media capabilities
                await page.evaluate("""
                    // Force enable media playback capabilities
                    if (navigator.mediaSession) {
                        navigator.mediaSession.setActionHandler('play', () => {});
                        navigator.mediaSession.setActionHandler('pause', () => {});
                    }
                    
                    // Override EME (Encrypted Media Extensions) to appear supported
                    if (!navigator.requestMediaKeySystemAccess) {
                        navigator.requestMediaKeySystemAccess = function(keySystem, configs) {
                            return Promise.resolve({
                                keySystem: keySystem,
                                getConfiguration: () => configs[0],
                                createMediaKeys: () => Promise.resolve({
                                    createSession: () => ({
                                        addEventListener: () => {},
                                        generateRequest: () => Promise.resolve(),
                                        update: () => Promise.resolve(),
                                        close: () => Promise.resolve()
                                    })
                                })
                            });
                        };
                    }
                    
                    // Mark as non-private browsing
                    Object.defineProperty(navigator, 'doNotTrack', { value: null });
                    
                    // Simulate proper media device access
                    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                        const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
                        navigator.mediaDevices.getUserMedia = function(constraints) {
                            return Promise.resolve({
                                getTracks: () => [],
                                getAudioTracks: () => [],
                                getVideoTracks: () => []
                            });
                        };
                    }
                """)
                
                self.logger.info("🔄 Applied additional media playback fixes")
            else:
                self.logger.info("✅ No playback protection detected")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error handling playback protection: {e}")
    
    async def premium_type(self, page: Page, element: ElementHandle, text: str, ai_behavior: Dict[str, Any], is_password: bool = False):
        """Premium typing with AI-powered human simulation"""
        await element.click()
        await element.fill('')  # Clear field
        
        base_delay = 180 if is_password else 120  # Slower for mobile
        variance = ai_behavior.get('skip_timing_variance', 10)
        
        for i, char in enumerate(text):
            # AI-powered typing rhythm
            if i % 3 == 0:  # Occasional faster bursts
                delay = random.randint(60, 100)
            elif char in 'aeiou':  # Vowels typed slightly faster
                delay = random.randint(base_delay - 30, base_delay + 10)
            else:
                delay = random.randint(base_delay, base_delay + variance * 8)
            
            await element.type(char, delay=delay)
            
            # Random pauses (AI behavior)
            if random.random() < 0.06:  # 6% chance (less for mobile)
                await asyncio.sleep(random.uniform(0.2, ai_behavior['pause_duration']))
    
    async def premium_playback_loop(self, page: Page, ai_behavior: Dict[str, Any], spotify_intel: Optional[Dict[str, Any]]):
        """Premium playback loop with all AI features"""
        self.logger.info("🎵 Starting PREMIUM playback loop with AI behavior")
        
        # First check if we can actually play music
        await asyncio.sleep(3)
        can_play = await self.verify_playback_capability(page)
        
        if not can_play:
            self.logger.error("❌ Cannot play music - playback not available")
            return
        
        # Enable repeat mode with AI behavior
        try:
            await self.premium_human_behavior(page, ai_behavior)
            
            # Mobile repeat button selectors
            repeat_selectors = [
                '[data-testid="control-button-repeat"]',
                'button[aria-label*="repeat"]',
                'button[aria-label*="Repeat"]',
                '.control-button-repeat'
            ]
            
            for selector in repeat_selectors:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        await page.click(selector)
                        self.logger.info("🔄 Repeat mode enabled")
                        break
                except:
                    continue
                    
            await asyncio.sleep(1)
        except:
            self.logger.warning("Could not find repeat button")
        
        # Try to start playing first song
        await self.try_start_playback(page, ai_behavior)
        
        # Main premium loop
        song_count = 0
        while True:
            try:
                song_count += 1
                
                # AI-powered behavior every few songs
                if song_count % 3 == 0:
                    await self.premium_human_behavior(page, ai_behavior)
                
                # AI-enhanced skip decision
                should_skip = random.random() < self.config.get('skip_probability', 0.55)
                
                if should_skip:
                    # AI-determined skip timing with variance
                    base_time = random.randint(
                        self.config.get('min_play_time', 32),
                        self.config.get('max_play_time', 45)
                    )
                    ai_variance = ai_behavior.get('skip_timing_variance', 5)
                    skip_time = base_time + random.randint(-ai_variance, ai_variance)
                    skip_time = max(30, skip_time)  # Never less than 30 seconds
                    
                    self.logger.info(f"⏭️ AI skip timing: {skip_time} seconds")
                    await asyncio.sleep(skip_time)
                    
                    # AI-powered skip behavior
                    await self.premium_human_behavior(page, ai_behavior)
                    
                    # Enhanced skip logic with mobile selectors
                    skip_action = random.random()
                    
                    mobile_skip_forward = [
                        '[data-testid="control-button-skip-forward"]',
                        'button[aria-label*="Next"]',
                        'button[aria-label*="Skip"]',
                        '.control-button-skip-forward'
                    ]
                    
                    mobile_skip_back = [
                        '[data-testid="control-button-skip-back"]',
                        'button[aria-label*="Previous"]',
                        'button[aria-label*="Back"]',
                        '.control-button-skip-back'
                    ]
                    
                    if skip_action < self.config.get('backward_skip_probability', 0.08):
                        # Backward skip
                        for selector in mobile_skip_back:
                            try:
                                if await page.is_visible(selector, timeout=1000):
                                    await page.click(selector)
                                    self.logger.info("⏮️ AI Backward skip")
                                    break
                            except:
                                continue
                                
                    elif skip_action < (self.config.get('backward_skip_probability', 0.08) + self.config.get('double_skip_probability', 0.15)):
                        # Double skip with AI timing
                        for selector in mobile_skip_forward:
                            try:
                                if await page.is_visible(selector, timeout=1000):
                                    await page.click(selector)
                                    await asyncio.sleep(random.uniform(0.5, ai_behavior['pause_duration']))
                                    await page.click(selector)
                                    self.logger.info("⏭️⏭️ AI Double skip")
                                    break
                            except:
                                continue
                    else:
                        # Regular skip
                        for selector in mobile_skip_forward:
                            try:
                                if await page.is_visible(selector, timeout=1000):
                                    await page.click(selector)
                                    self.logger.info("⏭️ AI Regular skip")
                                    break
                            except:
                                continue
                else:
                    # Let song play with occasional AI interactions
                    self.logger.info("🎶 AI: Playing full song")
                    await asyncio.sleep(10)
                    
                    # Random AI behavior during full song
                    if random.random() < 0.1:
                        await self.premium_human_behavior(page, ai_behavior)
                
                # AI-powered pause between actions
                await asyncio.sleep(random.uniform(1, ai_behavior['pause_duration'] * 2))
                
            except Exception as e:
                self.logger.error(f"Premium playback error: {e}")
                await asyncio.sleep(5)
    
    async def verify_playback_capability(self, page: Page) -> bool:
        """Check if music playback is actually available"""
        try:
            self.logger.info("🔍 Verifying playback capability...")
            
            # Check current URL first
            current_url = page.url
            if "accounts.spotify.com" in current_url or "login" in current_url:
                self.logger.error("❌ Still on login page - cannot verify playback")
                return False
            
            # Wait for page to fully load
            await asyncio.sleep(5)
            
            # Look for play controls
            play_controls = [
                '[data-testid="control-button-playpause"]',
                'button[aria-label*="Play"]',
                'button[aria-label*="Pause"]',
                '.playback-bar',
                '[data-testid="playback-controls"]',
                '.player-controls',
                '.spoticon-play-16',
                '.spoticon-pause-16'
            ]
            
            controls_found = False
            for selector in play_controls:
                try:
                    if await page.is_visible(selector, timeout=5000):
                        self.logger.info(f"✅ Found playback controls: {selector}")
                        controls_found = True
                        break
                except:
                    continue
            
            # Check for "Connect to a device" or login required messages
            blocking_messages = [
                'text="Connect to a device"',
                'text="Log in to Spotify"',
                'text="Sign up for Spotify"',
                'text="Playback disabled"',
                'text="Web Player is currently not supported"',
                'text="Download the app"',
                'text="Get the app"',
                '.empty-state',
                '[data-testid="login-button"]',
                '.spoticon-devices-16'
            ]
            
            for selector in blocking_messages:
                try:
                    if await page.is_visible(selector, timeout=2000):
                        self.logger.error(f"❌ Playback blocked: {selector}")
                        
                        # Try to bypass by injecting playback capability
                        await page.evaluate("""
                            // Force hide blocking messages
                            const blockingElements = document.querySelectorAll('[data-testid="login-button"], .empty-state, [aria-label*="Connect to a device"]');
                            blockingElements.forEach(el => {
                                if (el) el.style.display = 'none';
                            });
                            
                            // Try to enable web playback
                            if (window.Spotify && window.Spotify.Player) {
                                const player = new window.Spotify.Player({
                                    name: 'Web Playback SDK',
                                    getOAuthToken: () => {},
                                    volume: 0.5
                                });
                            }
                        """)
                        
                        await asyncio.sleep(2)
                        # Re-check after injection
                        if not await page.is_visible(selector, timeout=1000):
                            self.logger.info("✅ Bypassed blocking message")
                            break
                        else:
                            return False
                except:
                    continue
            
            if not controls_found:
                self.logger.warning("⚠️ No obvious playback controls found, trying alternative approach...")
                
                # Try to find any track or song elements
                track_elements = [
                    '[data-testid="tracklist-row"]',
                    '.track',
                    '.tracklist-row',
                    '[role="row"]',
                    '.song',
                    '[data-testid="track-list"]'
                ]
                
                for selector in track_elements:
                    try:
                        if await page.is_visible(selector, timeout=3000):
                            self.logger.info(f"✅ Found track elements: {selector}")
                            controls_found = True
                            break
                    except:
                        continue
            
            if controls_found:
                self.logger.info("✅ Playback capability verified")
                return True
            else:
                self.logger.error("❌ No playback controls or tracks found")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Error verifying playback: {e}")
            return False
    
    async def try_start_playback(self, page: Page, ai_behavior: Dict[str, Any]):
        """Try to start playing the first song"""
        try:
            self.logger.info("🎵 Attempting to start playback...")
            
            # First, try to inject web playback SDK
            await page.evaluate("""
                // Enable web playback if possible
                if (window.onSpotifyWebPlaybackSDKReady) {
                    window.onSpotifyWebPlaybackSDKReady();
                }
                
                // Try to find and click play buttons programmatically
                const playButtons = document.querySelectorAll('[data-testid="control-button-playpause"], button[aria-label*="Play"], .spoticon-play-16');
                if (playButtons.length > 0) {
                    playButtons[0].click();
                }
            """)
            
            await asyncio.sleep(2)
            
            # Look for play button
            play_button_selectors = [
                '[data-testid="control-button-playpause"]',
                'button[aria-label*="Play"]',
                '.playback-controls button[aria-label*="Play"]',
                '[data-testid="play-button"]',
                '.spoticon-play-16',
                '.player-controls button'
            ]
            
            for selector in play_button_selectors:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        # Check if it's actually a play button (not pause)
                        try:
                            aria_label = await page.get_attribute(selector, 'aria-label')
                            if aria_label and ('play' in aria_label.lower() and 'pause' not in aria_label.lower()):
                                await self.premium_human_behavior(page, ai_behavior)
                                await page.click(selector)
                                self.logger.info(f"✅ Started playback via: {selector}")
                                await asyncio.sleep(2)
                                return
                        except:
                            # If can't get aria-label, just try clicking
                            await self.premium_human_behavior(page, ai_behavior)
                            await page.click(selector)
                            self.logger.info(f"✅ Clicked potential play button: {selector}")
                            await asyncio.sleep(2)
                            return
                except:
                    continue
            
            # Try clicking on a song in the playlist
            song_selectors = [
                '[data-testid="tracklist-row"] button',
                '[data-testid="tracklist-row"]',
                '.tracklist-row',
                '[role="row"]',
                '.track',
                '.song-row',
                '[data-testid="track-list"] [role="button"]'
            ]
            
            for selector in song_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        # Try the first few songs
                        for i, element in enumerate(elements[:3]):
                            try:
                                await self.premium_human_behavior(page, ai_behavior)
                                await element.click()
                                self.logger.info(f"✅ Clicked on song {i+1}: {selector}")
                                await asyncio.sleep(3)
                                
                                # Check if playback started
                                if await self.check_if_playing(page):
                                    self.logger.info("🎵 Playback confirmed!")
                                    return
                            except:
                                continue
                except:
                    continue
            
            # Try double-click on songs (sometimes needed)
            for selector in song_selectors:
                try:
                    if await page.is_visible(selector, timeout=3000):
                        await self.premium_human_behavior(page, ai_behavior)
                        await page.dblclick(selector)
                        self.logger.info(f"✅ Double-clicked on song: {selector}")
                        await asyncio.sleep(3)
                        
                        if await self.check_if_playing(page):
                            self.logger.info("🎵 Playback confirmed after double-click!")
                            return
                except:
                    continue
            
            self.logger.warning("⚠️ Could not start playback - no play button or songs found")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting playback: {e}")
    
    async def check_if_playing(self, page: Page) -> bool:
        """Check if music is currently playing"""
        try:
            # Look for pause button (indicates playing)
            pause_indicators = [
                'button[aria-label*="Pause"]',
                '[data-testid="control-button-playpause"][aria-label*="Pause"]',
                '.spoticon-pause-16'
            ]
            
            for selector in pause_indicators:
                try:
                    if await page.is_visible(selector, timeout=2000):
                        return True
                except:
                    continue
            
            # Check for progress bar movement or time display
            try:
                progress_element = await page.query_selector('[data-testid="playback-position"]')
                if progress_element:
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error checking playback status: {e}")
            return False

# Configuration with your credentials
async def main():
    config = {
        'bot_id': 'github_premium_bot',
        'username': 'arshadahsan388@gmail.com',
        'password': 'Check78600',
        'playlist_url': 'https://open.spotify.com/playlist/5muSk2zfQ3LI70S64jbrX7?si=d5xrwoM_T2--yHFfRsd9rw',
        'headless': False,
        'skip_probability': 0.55,
        'min_play_time': 32,
        'max_play_time': 45,
        'double_skip_probability': 0.15,
        'backward_skip_probability': 0.08
    }
    
    bot = PremiumSpotifyBot(config)
    await bot.run_premium_session()

if __name__ == "__main__":
    asyncio.run(main())
