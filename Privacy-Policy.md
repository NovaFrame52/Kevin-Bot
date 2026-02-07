# Privacy Policy for Kevin Discord Bot

**Last Updated: February 7, 2026**

## 1. Introduction

This Privacy Policy explains how the Kevin Discord bot ("Kevin", "the Bot", "we", "us") collects, uses, and protects information when you use our service. We are committed to transparency about our data practices.

## 2. Information We Collect

### 2.1 Automatically Collected Information

When Kevin operates in your Discord server, the Bot automatically collects:

- **User Information**: Discord user ID, username, and display name of users who interact with the Bot
- **Server Information**: Server/guild ID, server name, and channel IDs where the Bot operates
- **Message Content**: Content of messages that invoke Bot commands (both prefix and slash commands)
- **Reminder Data**: User-provided reminder messages, times, and associated user IDs
- **Command Usage**: Records of which commands are used, when, and by whom
- **Moderation Actions**: Logs of moderation commands (kick, ban, mute, purge) including targets and reasons
- **Timestamps**: When interactions and events occur

### 2.2 Log Data

Kevin maintains detailed logs for debugging and operational purposes, stored locally in files named `Kevin_Log_*.txt`. These logs may include:

- Command invocations and Bot responses
- Error messages and stack traces
- User IDs, channel IDs, and server IDs
- Timestamps of all events
- Moderation actions and their outcomes
- Website monitoring status checks and alerts
- Bot startup and shutdown events

### 2.3 Persistent Storage

Kevin stores certain data persistently in local files:

- **Reminder Data**: Stored in `persistent_reminders.json` including user IDs, reminder messages, and scheduled times
- **Server Configurations**: Stored in `configs.json` including per-server prefixes, mod roles, log channels, and welcome channels
- **Log Files**: Rotating log files stored in the configured desktop/log directory

### 2.4 Information We Do NOT Collect

Kevin does not collect, store, or process:

- Message content from messages that don't invoke the Bot
- Private conversations between users
- User email addresses or personal contact information beyond Discord usernames
- Voice chat data or recordings
- Attachments or media files (except temporarily to relay DM attachments)
- Messages in channels where the Bot lacks access
- Data from servers where the Bot is not present

## 3. How We Use Information

We use collected information solely for the following purposes:

- **Bot Operation**: To execute commands, deliver reminders, and provide Bot functionality
- **Reminder System**: To store and deliver reminders at requested times
- **Moderation**: To execute moderation commands and log moderation actions
- **Server Configuration**: To remember per-server settings (prefixes, roles, channels)
- **Website Monitoring**: To check website availability and send alerts
- **Logging & Debugging**: To diagnose issues, monitor performance, and improve the Bot
- **Command Authentication**: To verify permissions for restricted commands

## 4. Data Storage and Retention

### 4.1 Storage Location

All data is stored locally on the server where Kevin is deployed:

- Log files: Stored in the directory specified by `KEVIN_DESKTOP_PATH` environment variable (default: `$HOME/Desktop`)
- Reminder data: Stored in `persistent_reminders.json` in the same directory
- Server configs: Stored in `configs.json` in the Bot's Scripts directory
- No data is transmitted to external servers or cloud services (except Discord's API for Bot operations)

### 4.2 Retention Period

- **Active Logs**: Log files are rotated when they reach 5MB, with up to 3 backup files retained
- **Reminder Data**: Stored until reminders are delivered or manually deleted by users
- **Server Configurations**: Retained indefinitely until manually deleted or the Bot is removed from a server
- **Historical Logs**: Old log files may accumulate unless manually deleted by the server administrator

### 4.3 Data Deletion

- Server administrators can delete log files and JSON data files at any time from their local filesystem
- Removing Kevin from a server immediately stops all data collection from that server
- Users can delete their own reminders using the appropriate commands
- Self-hosters have full control over all data stored by their deployment

## 5. Data Sharing and Disclosure

### 5.1 Third-Party Sharing

We do NOT sell, trade, rent, or share your data with third parties for marketing or any other purposes.

### 5.2 Discord Platform

Kevin uses Discord's API to function and necessarily shares data with Discord according to Discord's own Privacy Policy and Terms of Service. This includes:

- Message content the Bot reads (for command processing)
- Responses the Bot sends to channels and users
- Slash command interactions
- DM messages sent via the Bot

### 5.3 Website Monitoring

When configured for website monitoring, the Bot makes HTTP requests to the monitored website. These requests originate from the server hosting the Bot and may be logged by the monitored website according to their own privacy policies.

### 5.4 Legal Requirements

We may disclose information if required by law, such as to comply with a subpoena or similar legal process. However, as Kevin is primarily self-hosted, server administrators control their own data.

## 6. Data Security

We take reasonable measures to protect collected data:

- Log files and data files are stored with standard file system permissions
- Access to the server is controlled by the server administrator
- The Bot runs under standard user privileges (or as configured)
- Environment variables (including the Discord token) are stored in `.env` files with restricted permissions (600)
- The installer automatically sets restrictive permissions on configuration files

However, no method of electronic storage is 100% secure. While we strive to protect your information, we cannot guarantee absolute security. Self-hosters are responsible for securing their own deployments.

## 7. Your Rights and Choices

### 7.1 Self-Hosted Deployments

Server administrators who self-host Kevin can:

- View, modify, or delete all log files and data files at any time
- Configure the Bot's behavior and data collection
- Control where data is stored via environment variables
- Access the complete source code to verify data handling practices
- Modify the Bot's code to change data collection practices

### 7.2 End Users

Discord users can:

- Use the Bot's commands to manage their own reminders
- Request that server administrators remove the Bot
- Leave servers where Kevin is present
- Avoid using the Bot's features to minimize data collection
- Request data deletion from server administrators

### 7.3 Data Access and Deletion Requests

To request information about data collected about you, or to request deletion:

- Contact the administrator of the server where Kevin is deployed
- For self-hosted instances, server administrators can directly access and delete data files
- Reminder data can be deleted using the Bot's reminder management commands (if implemented)

## 8. Children's Privacy

Kevin does not knowingly collect information from children under 13 (or the applicable age in your jurisdiction). The Bot relies on Discord's age verification. If you believe we have inadvertently collected information from a child, please contact the server administrator.

## 9. Open Source Transparency

Kevin is open source software released under the MIT License. You can review the complete source code to verify:

- What data is collected
- How data is processed and stored
- Where data is stored
- How data is used
- Security practices implemented

The source code is available in the project repository and can be audited by anyone.

## 10. Discord's Policies

Kevin operates on Discord's platform and is subject to:

- Discord's Privacy Policy
- Discord's Terms of Service
- Discord's Developer Terms of Service
- Discord's Community Guidelines

We recommend reviewing Discord's privacy documentation at https://discord.com/privacy

## 11. Self-Hosting Considerations

If you self-host Kevin, you should be aware:

- You are the data controller for your deployment
- You are responsible for securing your environment and configuration files
- You must protect your Discord bot token (stored in `kevin.env`)
- You are responsible for managing and securing log files
- You should configure appropriate file permissions and access controls
- You should regularly review and clean up log files to prevent excessive data accumulation

## 12. International Users

Kevin may be deployed on servers located in various jurisdictions. Data is stored locally on the server where the Bot runs. By using the Bot, you consent to the transfer and processing of your information in the jurisdiction where that specific Bot deployment is located.

## 13. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. Changes will be indicated by updating the "Last Updated" date at the top of this policy. Material changes will be communicated through:

- Updates to the project repository
- Documentation in the README file
- Notifications to server administrators (where feasible)

Continued use of Kevin after changes constitutes acceptance of the updated Privacy Policy.

## 14. Data Breach Notification

In the event of a data breach affecting user information:

- Self-hosters are responsible for their own breach response
- For any managed instances, we will assess the scope and impact
- We will take immediate steps to secure systems
- We will notify affected parties as required by applicable law

However, given Kevin's self-hosted nature, individual deployments are the responsibility of their operators.

## 15. Specific Data Practices

### 15.1 Reminder System

- Reminder messages and times are stored in `persistent_reminders.json`
- This file contains user IDs, reminder text, and scheduled delivery times
- Reminders are delivered via Discord DM or channel messages
- Failed delivery attempts are logged but reminders may not be re-attempted

### 15.2 Moderation Logging

- Moderation actions (kicks, bans, mutes, purges) are logged with user IDs and reasons
- Logs may be sent to configured log channels if set up by administrators
- Moderation logs are retained in log files according to the retention policy
- Server administrators are responsible for managing moderation logs appropriately

### 15.3 Website Monitoring

- The Bot makes HTTP requests to monitored websites at configured intervals
- Request outcomes (success/failure, status codes) are logged
- Alerts are sent to configured channels or users when sites appear down
- The monitored website may log the Bot's requests according to their own policies

### 15.4 DM Functionality

- The DM command allows authorized users to send messages to server members
- DM content is temporarily processed but not permanently stored (beyond standard logs)
- Image attachments are relayed through Discord's infrastructure
- Use of DM functionality is restricted by the `ALLOWED_DM_USER_ID` configuration

## 16. GDPR Compliance (European Users)

For users in the European Economic Area, you have the following rights under GDPR:

- **Right to Access**: Request copies of your data from server administrators
- **Right to Rectification**: Request correction of inaccurate data
- **Right to Erasure**: Request deletion of your data (contact server administrator)
- **Right to Restrict Processing**: Request limited processing of your data
- **Right to Data Portability**: Request transfer of your data
- **Right to Object**: Object to processing of your data

To exercise these rights, contact the administrator of the server where Kevin is deployed. For self-hosted instances, administrators can directly access and modify data files.

## 17. California Privacy Rights (CCPA)

California residents have the right to:

- Know what personal information is collected
- Know whether personal information is sold or disclosed (we do not sell data)
- Opt-out of the sale of personal information (not applicable as we don't sell data)
- Request deletion of personal information
- Non-discrimination for exercising privacy rights

Contact your server administrator to exercise these rights.

## 18. Limitations

This Privacy Policy applies only to Kevin and does not cover:

- Other bots on the same Discord server
- Discord's own data practices
- Third-party services or websites monitored by the Bot
- Other software or services you may use
- Data practices of individual self-hosted deployments (beyond what the code implements)

## 19. Contact Information

For questions, concerns, or requests regarding this Privacy Policy or your data:

- Contact the administrator of the server where Kevin is deployed
- For self-hosted instances, you control all data directly
- File an issue in the project's code repository for questions about data practices
- Review the source code to verify data handling

## 20. Responsibility for Self-Hosted Instances

While this Privacy Policy describes the data practices implemented in Kevin's source code, individual server administrators who self-host the Bot are responsible for:

- Their own privacy policies and notices to users
- Compliance with applicable privacy laws in their jurisdiction
- Securing their deployment and protecting stored data
- Managing data retention and deletion
- Responding to data access and deletion requests from their users

---

**By using Kevin, you acknowledge that you have read and understood this Privacy Policy.**