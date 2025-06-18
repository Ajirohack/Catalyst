// Catalyst DOM Selector Verification Script
// This script helps verify DOM selectors across supported platforms
// To use, paste this in the browser console when on a supported platform
// Version 1.0.0 - June 17, 2025

(function () {
    console.log("Catalyst DOM Selector Verification Tool");
    console.log("======================================");

    // Get current domain
    const hostname = window.location.hostname;
    console.log("Current domain:", hostname);

    // Platform selectors
    const PLATFORM_SELECTORS = {
        'web.whatsapp.com': {
            messageContainer: '[data-testid="conversation-panel-messages"]',
            messages: '[data-testid="msg-container"]',
            messageText: '.selectable-text span',
            sender: '[data-testid="msg-meta"] span[dir="auto"]',
            timestamp: '[data-testid="msg-meta"] span[title]',
            inputField: '[data-testid="conversation-compose-box-input"]',
            sendButton: '[data-testid="compose-btn-send"]'
        },
        'www.messenger.com': {
            messageContainer: '[role="main"] [data-testid="conversation"]',
            messages: '[data-testid="message_container"]',
            messageText: '[data-testid="message_text"]',
            sender: '[data-testid="message_sender"]',
            timestamp: '[data-testid="message_timestamp"]',
            inputField: '[contenteditable="true"][role="textbox"]',
            sendButton: '[data-testid="send_button"]'
        },
        'instagram.com': {
            messageContainer: 'div[role="dialog"] div[style*="overflow-y: auto"]',
            messages: 'div[role="row"]',
            messageText: 'div[style*="max-width"] > div > div > span',
            sender: 'div[role="row"] h4',
            timestamp: 'time',
            inputField: 'div[contenteditable="true"]',
            sendButton: 'button[type="submit"]'
        },
        'discord.com': {
            messageContainer: '[data-list-id="chat-messages"]',
            messages: '[class*="message-"]',
            messageText: '[class*="messageContent-"]',
            sender: '[class*="username-"]',
            timestamp: '[class*="timestamp-"]',
            inputField: '[class*="textArea-"] [class*="scrollableContainer-"] [role="textbox"]',
            sendButton: 'button[type="submit"]'
        },
        'slack.com': {
            messageContainer: '.c-virtual_list__scroll_container',
            messages: '.c-message_kit__message',
            messageText: '.p-rich_text_section',
            sender: '.c-message__sender_button',
            timestamp: '.c-timestamp',
            inputField: '[contenteditable="true"][role="textbox"]',
            sendButton: 'button[aria-label="Send message"]'
        },
        'teams.microsoft.com': {
            messageContainer: '.ts-message-list-container',
            messages: '.ts-message',
            messageText: '.message-body-content',
            sender: '.ts-message-sender',
            timestamp: '.message-datetime',
            inputField: '[contenteditable="true"][role="textbox"]',
            sendButton: 'button[aria-label="Send"]'
        },
        'web.telegram.org': {
            messageContainer: '.messages-container',
            messages: '.message',
            messageText: '.message-text',
            sender: '.message-author',
            timestamp: '.message-date',
            inputField: '.composer-input',
            sendButton: '.btn-send'
        },
        'chat.openai.com': {
            messageContainer: '.flex.flex-col.items-center.text-sm',
            messages: '.markdown',
            messageText: '.markdown p',
            sender: '.font-semibold',
            timestamp: '.text-gray-400',
            inputField: 'textarea',
            sendButton: 'button[data-testid="send-button"]'
        },
        'mail.google.com': {
            messageContainer: '.Bs.nH.iY.bAt',
            messages: '.gs',
            messageText: '.a3s.aiL',
            sender: '.gD',
            timestamp: '.g3',
            inputField: '[role="textbox"]',
            sendButton: '[data-tooltip="Send ‪(⌘Enter)‬"]'
        },
        'www.linkedin.com': {
            messageContainer: '.msg-conversations-container__conversations-list',
            messages: '.msg-s-message-list__event',
            messageText: '.msg-s-event-listitem__body',
            sender: '.msg-s-message-group__name',
            timestamp: '.msg-s-message-group__timestamp',
            inputField: '.msg-form__contenteditable',
            sendButton: '.msg-form__send-button'
        },
        'twitter.com': {
            messageContainer: '.css-1dbjc4n.r-1jgb5lz.r-1ye8kvj',
            messages: '[data-testid="messageEntry"]',
            messageText: '[data-testid="tweetText"]',
            sender: '[data-testid="User-Name"]',
            timestamp: '[data-testid="timestamp"]',
            inputField: '[data-testid="dmComposerTextInput"]',
            sendButton: '[data-testid="dmComposerSendButton"]'
        },
        'outlook.live.com': {
            messageContainer: '[role="main"]',
            messages: '.ReadMsgContainer',
            messageText: '.ReadMsgBody',
            sender: '.ReadMsgHeaderFrom',
            timestamp: '.ReadMsgHeaderDate',
            inputField: '[aria-label="Message body"]',
            sendButton: '[aria-label="Send"]'
        },
        'reddit.com': {
            messageContainer: '.ListingLayout-backgroundContainer',
            messages: '.ChatMessageThread__messageContainer',
            messageText: '.ChatMessageContent',
            sender: '.ChatMessageHeader__username',
            timestamp: '.ChatMessageHeader__timestamp',
            inputField: '.ChatComposer__textarea',
            sendButton: '.ChatSubmitButton'
        },
        'meet.google.com': {
            messageContainer: '.z38b6',
            messages: '.GDhqjd',
            messageText: '.oIy2qc',
            sender: '.YTbUzc',
            timestamp: '.MuzmKe',
            inputField: '.KHxj8b',
            sendButton: '.VfPpkd-Bz112c-LgbsSe'
        },
        'zoom.us': {
            messageContainer: '.chat-list__container',
            messages: '.chat-message__container',
            messageText: '.chat-message__text',
            sender: '.chat-message__sender',
            timestamp: '.chat-message__time',
            inputField: '.chat-composer__input',
            sendButton: '.chat-composer__send-btn'
        },
        'web.skype.com': {
            messageContainer: '.ConversationView',
            messages: '.message',
            messageText: '.content',
            sender: '.sender',
            timestamp: '.timestamp',
            inputField: '[role="textbox"]',
            sendButton: '.send-button'
        }
    };

    // Verify selectors for current domain
    function verifyDomSelectors() {
        // Find the matching domain
        const matchingDomain = Object.keys(PLATFORM_SELECTORS).find(domain => {
            return hostname.includes(domain);
        });

        if (!matchingDomain) {
            console.error("❌ Current domain not supported:", hostname);
            return {
                success: false,
                error: "Domain not supported",
                domain: hostname
            };
        }

        console.log("✅ Found matching domain:", matchingDomain);
        const selectors = PLATFORM_SELECTORS[matchingDomain];

        // Check each selector
        const results = {
            domain: matchingDomain,
            success: true,
            selectors: {}
        };

        for (const [name, selector] of Object.entries(selectors)) {
            try {
                const elements = document.querySelectorAll(selector);
                const found = elements.length > 0;

                results.selectors[name] = {
                    selector,
                    found,
                    count: elements.length
                };

                if (found) {
                    console.log(`✅ Found ${elements.length} elements for '${name}' using selector: ${selector}`);
                } else {
                    console.warn(`⚠️ No elements found for '${name}' using selector: ${selector}`);
                    results.success = false;
                }
            } catch (error) {
                console.error(`❌ Error testing selector '${name}': ${error.message}`);
                results.selectors[name] = {
                    selector,
                    found: false,
                    error: error.message
                };
                results.success = false;
            }
        }

        return results;
    }

    // Show results in console
    const results = verifyDomSelectors();
    console.log("======================================");
    console.log("Verification Results:", results);

    // Create visual report on the page
    function createVisualReport(results) {
        // Remove existing report if any
        const existingReport = document.getElementById('catalyst-selector-report');
        if (existingReport) {
            existingReport.remove();
        }

        // Create report container
        const reportDiv = document.createElement('div');
        reportDiv.id = 'catalyst-selector-report';
        reportDiv.style.position = 'fixed';
        reportDiv.style.top = '20px';
        reportDiv.style.right = '20px';
        reportDiv.style.width = '350px';
        reportDiv.style.maxHeight = '80vh';
        reportDiv.style.overflow = 'auto';
        reportDiv.style.backgroundColor = '#fff';
        reportDiv.style.border = '1px solid #ccc';
        reportDiv.style.borderRadius = '5px';
        reportDiv.style.padding = '15px';
        reportDiv.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
        reportDiv.style.zIndex = '10000';
        reportDiv.style.fontFamily = 'Arial, sans-serif';

        // Add header
        const header = document.createElement('div');
        header.innerHTML = `
      <h2 style="margin-top: 0; color: #2c3e50;">Catalyst Selector Verification</h2>
      <p><strong>Domain:</strong> ${results.domain}</p>
      <p><strong>Overall:</strong> ${results.success ?
                '<span style="color: green;">✅ All selectors working</span>' :
                '<span style="color: orange;">⚠️ Some selectors need fixing</span>'}</p>
    `;
        reportDiv.appendChild(header);

        // Add selector results
        const selectorResults = document.createElement('div');
        selectorResults.innerHTML = '<h3 style="border-bottom: 1px solid #eee; padding-bottom: 8px;">Selector Results</h3>';

        const table = document.createElement('table');
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';

        // Add table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
      <tr>
        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #eee;">Selector</th>
        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #eee;">Status</th>
        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #eee;">Count</th>
      </tr>
    `;
        table.appendChild(thead);

        // Add table body
        const tbody = document.createElement('tbody');
        for (const [name, info] of Object.entries(results.selectors)) {
            const row = document.createElement('tr');
            row.innerHTML = `
        <td style="padding: 8px; border-bottom: 1px solid #eee;">${name}</td>
        <td style="text-align: center; padding: 8px; border-bottom: 1px solid #eee; color: ${info.found ? 'green' : 'red'};">
          ${info.found ? '✅' : '❌'}
        </td>
        <td style="text-align: center; padding: 8px; border-bottom: 1px solid #eee;">${info.count || 0}</td>
      `;
            tbody.appendChild(row);
        }
        table.appendChild(tbody);
        selectorResults.appendChild(table);
        reportDiv.appendChild(selectorResults);

        // Add close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.marginTop = '15px';
        closeButton.style.padding = '8px 15px';
        closeButton.style.backgroundColor = '#3498db';
        closeButton.style.color = 'white';
        closeButton.style.border = 'none';
        closeButton.style.borderRadius = '4px';
        closeButton.style.cursor = 'pointer';
        closeButton.onclick = () => reportDiv.remove();
        reportDiv.appendChild(closeButton);

        // Add to page
        document.body.appendChild(reportDiv);
    }

    // Show visual report
    createVisualReport(results);

    // Return results for further processing
    return results;
})();
