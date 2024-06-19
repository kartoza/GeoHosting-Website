## Geohosting

products app

#### License

# Geohosting Setup Guide

Welcome to the Geohosting setup guide. This document will help you set up Geohosting on your local machine by installing the necessary components: Frappe-bench, MariaDB, and ERPNext.

## Prerequisites

_Before you begin, ensure you have the following:_

- A machine running Ubuntu
- Basic knowledge of terminal commands

### Installation Steps

To set up Geohosting on your local machine, follow these steps:

1. **Install Frappe-bench**
Frappe-bench is a command-line tool to manage Frappe deployments. To install it, follow the instructions provided in the link below.

2. **Install MariaDB**
MariaDB is a popular database server. It will be used as the database backend for ERPNext. The installation instructions are included in the link below.

3. **Install ERPNext**
ERPNext is an open-source ERP solution that will be used for Geohosting. The detailed steps for its installation are also covered in the link below.

## Detailed Installation Guide
For a comprehensive guide on how to install Frappe-bench, MariaDB, and ERPNext on your system, please refer to the following link:

[Installation Guide](https://github.com/D-codE-Hub/Frappe-ERPNext-Version-15--in-Ubuntu-22.04-LTS/blob/main/README.md)

This guide provides step-by-step instructions, including necessary commands and configurations, to ensure a smooth setup process.

### Add currentsite.txt file if does not exist

To ensure the currentsite.txt file exists in the sites directory and contains the text dcode.com, follow these steps:

1. Navigate to the `sites` Directory:

```sh
cd /frappe-bench/sites
```

2. Check if currentsite.txt Exists:

```sh
if [ ! -f currentsite.txt ]; then
    echo "dcode.com" > currentsite.txt
    echo "currentsite.txt created and dcode.com added."
else
    echo "currentsite.txt already exists."
fi
```
### Install the repository as a custom app in the frappe-bench

**Step 1:** Navigate to the Apps Directory

First, open your terminal and navigate to the apps directory within your Frappe bench setup.

```sh
cd /frappe-bench/apps
```
**Step 2:** Download the Custom App

Use the bench get-app command to download the app from the git repository.

```sh
bench get-app [repo-link]

for GeoHosting-Website

bench get-app https://github.com/kartoza/GeoHosting-Website

```

**Step 4:** Install the Custom App

Now you need to install the app into your site. Use the bench install-app command, specifying the name of the app you want to install.

```sh
bench install-app [app-name]

for GeoHosting-Website

bench install-app geohosting

```

To access GeoHosting on your local machine, open your web browser and go to:

http://127.0.0.1:8000/main/products.html

>Note: Your local host address or port may be different. If the above URL does not work, try using:

http://localhost/main/products.html

### Install the other repositories as custom apps in the frappe bench

**Handle Installation Errors**

If you encounter any errors while getting or installing the app, the terminal will show you the specific error indicating which app is not installed. You can resolve this issue by installing the required app first. Use the following commands to install the necessary apps:

#### Frappe Paystack

```sh

bench get-app https://github.com/voogt/frappe_paystack

bench install-app geohosting

```

#### Payments

```sh

bench get-app  https://github.com/frappe/payments

bench install-app payments

```

#### Kartoza Custom

```sh

bench get-app https://github.com/voogt/kartoza_custom

bench install-app kartoza_custom

```


#### E-commerce Integrations

```sh

bench get-app https://github.com/frappe/ecommerce_integrations

bench install-app ecommerce_integrations

```
