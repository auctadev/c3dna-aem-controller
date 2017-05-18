![C3DNA Logo](https://raw.githubusercontent.com/clc-runner/Assets/master/c3dna.png)

### Summary
C3DNA Controller brings end-to-end Application Lifecycle Management to Enterprise Private or Hybrid Clouds. Both existing traditional monolithic apps (e.g. pets) as well as modern, cloud-native applications (e.g. cattle) can be deployed to multiple clouds and managed via policies that provide developers and application owners with application-centric visibility and dynamic, policy-based real-time management with instant cross-cloud workload portability.  

C3DNA Controller for Adobe Experience Manager (AEM) is a (licensed) virtual appliance that includes the pre-installed Adobe Experience Manager (AEM) software. (License for AEM *not* included. Customer should contact Adobe or a reseller for an AEM license.)

### Description
This runner playbook will install the C3DNA Controller, the primary control server in a C3DNA deployment, used for managing one or more C3DNA Platform nodes (e.g. hosts). Get the [C3DNA Platform virtual appliance here](https://www.ctl.io/marketplace/partner/DIME/product/C3DNA%20AEM%20Controller/).

### Additional Information
To learn more about the C3DNA platform, check out this [Intro Video](http://c3dna.com/videos.html).

### Deployment Process
This Runner job performs the following steps:

1. Provisions a C3DNA Controller virtual appliance (with the AEM software pre-installed) in the customer's CenturyLink Cloud account and initiates a monthly recurring subscription.

### Prerequisite(s)
* Access to the CenturyLink Cloud platform as an authorized user.

### Postrequisite(s)
* Customer must their own Adobe Experience Manager license.

### Frequently Asked Questions (FAQ)

#### Will executing this Runner job charge my CenturyLink Cloud account?
Yes, executing this Runner job will initiate a recurring monthly subscription for the C3DNA Controller.

#### Who should I contact for support?
* Please send C3DNA support requests to: [support@c3dna.com](mailto:support@c3dna.com).
* For issues related to CenturyLink Cloud infrastructure (VMs, network, etc.), please open a support ticket by emailing [help@ctl.io](mailto:help@ctl.io) or [through the support website](https://t3n.zendesk.com/tickets/new).

#### How difficult is it to deploy?
Click the "Run" button to begin the deployment process. Then, populate the Runner job user-input fields with the following:
* Datacenter, Network (VLAN), and Server Group
* Server Name
* V1 API credentials
* CenturyLink Cloud credentials

After updating the form fields, click the "Run" button again to initiate the C3DNA Controller for AEM virtual appliance deployment.
