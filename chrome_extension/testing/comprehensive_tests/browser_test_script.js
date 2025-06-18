// Catalyst Whisper Coach - Browser Test Script
// Paste this script in the browser console to test the extension on a platform

(function() {
  console.clear();
  console.log('%c Catalyst Whisper Coach - Platform Testing', 'font-weight: bold; font-size: 16px; color: #6772e5;');
  
  // Current hostname and URL
  const hostname = window.location.hostname;
  const url = window.location.href;
  console.log('%cTesting platform:', 'font-weight: bold', hostname);
  console.log('URL:', url);
  
  // Check if extension is loaded
  if (typeof window.catalystInjected === 'undefined') {
    console.log('%c❌ Extension not detected on this page!', 'color: red; font-weight: bold');
    console.log('Make sure the extension is loaded and permissions are granted for this domain.');
    return false;
  }
  
  console.log('%c✅ Extension detected!', 'color: green; font-weight: bold');
  
  // Platform detection
  let platformName = 'unknown';
  if (hostname.includes('whatsapp')) platformName = 'WhatsApp';
  else if (hostname.includes('messenger')) platformName = 'Facebook Messenger';
  else if (hostname.includes('instagram')) platformName = 'Instagram';
  else if (hostname.includes('discord')) platformName = 'Discord';
  else if (hostname.includes('slack')) platformName = 'Slack';
  else if (hostname.includes('teams')) platformName = 'Microsoft Teams';
  else if (hostname.includes('telegram')) platformName = 'Telegram';
  else if (hostname.includes('meet.google')) platformName = 'Google Meet';
  else if (hostname.includes('zoom')) platformName = 'Zoom';
  else if (hostname.includes('chat.openai')) platformName = 'ChatGPT';
  else if (hostname.includes('mail.google')) platformName = 'Gmail';
  else if (hostname.includes('linkedin')) platformName = 'LinkedIn';
  else if (hostname.includes('twitter') || hostname.includes('x.com')) platformName = 'Twitter/X';
  else if (hostname.includes('outlook')) platformName = 'Outlook';
  else if (hostname.includes('reddit')) platformName = 'Reddit';
  else if (hostname.includes('skype')) platformName = 'Skype';
  
  console.log('Detected platform:', platformName);
  
  // Check content script functions
  if (typeof window.catalystDebug !== 'undefined') {
    console.log('%c✅ Debug helpers available!', 'color: green');
    
    console.log('\n%cTesting DOM selectors...', 'font-weight: bold');
    const selectorResults = window.catalystDebug.testSelectors();
    console.log('Selector test results:', selectorResults);
    
    // Test message detection
    console.log('\n%cTesting message detection...', 'font-weight: bold');
    const messages = window.catalystDebug.logMessages(3);
    if (messages && messages.length > 0) {
      console.log('%c✅ Detected ' + messages.length + ' messages!', 'color: green');
      console.log('Sample messages:', messages);
    } else {
      console.log('%c❌ No messages detected', 'color: orange');
      console.log('Either there are no messages in the conversation or selectors might need adjustment.');
    }
    
    // Test whisper generation
    console.log('\n%cTesting whisper generation...', 'font-weight: bold');
    console.log('Requesting a test whisper suggestion...');
    
    window.catalystDebug.forceSuggestion("I'm feeling upset about what happened yesterday")
      .then(response => {
        if (response && response.suggestions) {
          console.log('%c✅ Whisper suggestion generated!', 'color: green');
          console.log('Suggestion:', response.suggestions[0]);
        } else {
          console.log('%c❌ Failed to generate whisper suggestion', 'color: red');
          console.log('Response:', response);
        }
      })
      .catch(error => {
        console.log('%c❌ Error generating whisper suggestion', 'color: red');
        console.log('Error:', error);
      });
  } else {
    console.log('%c❌ Debug helpers not available!', 'color: red');
    console.log('Make sure content_script.js includes the debug helpers.');
  }
  
  // Return test status
  return {
    extensionDetected: typeof window.catalystInjected !== 'undefined',
    debugHelpersAvailable: typeof window.catalystDebug !== 'undefined',
    platform: platformName,
    url: url,
    timestamp: new Date().toISOString()
  };
})();
