# Moodle LMS on AWS using CDK (Python)

[![CDK](https://img.shields.io/badge/AWS%20CDK-Python-blue)](https://docs.aws.amazon.com/cdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203.11-blue)](https://www.python.org/)
[![Deployed on AWS](https://img.shields.io/badge/Deployed%20on-AWS-orange)](https://aws.amazon.com/)

This project provisions a complete Moodle Learning Management System (LMS) deployment using **AWS Cloud Development Kit (CDK)** with Python. It includes all infrastructure components necessary to host a production-grade Moodle installation, including EC2, Aurora MySQL, and an Application Load Balancer (ALB).

---

## 🚀 Project Highlights

- ✅ Infrastructure-as-Code with AWS CDK (Python)
- 🧱 Secure VPC with public/private subnets across 2 AZs
- 🖥️ EC2 instance with Apache, PHP 8.1, and Moodle 4.1 LTS
- 🛡️ IAM roles and Systems Manager (SSM) — no SSH exposure
- 📶 Application Load Balancer (ALB) for high availability
- 🔐 Aurora MySQL DB with credentials in Secrets Manager
- 📄 Auto-configured User Data installs and prepares Moodle

---

## 🧰 Architecture Overview

![Architecture Diagram](https://raw.githubusercontent.com/your-username/moodle-lms-on-aws/main/assets/moodle_architecture.png)

```
           +--------------------------+
           |   Application Load Balancer  |
           +------------+-------------+
                        |
                 [HTTP traffic]
                        |
                +-------v-------+
                |     EC2 (Moodle)     |
                | Apache + PHP + SSM  |
                +---+-----------+----+
                    |           |
            +-------v--+   +----v------+
            | MoodleDir |   |  AuroraDB  |
            +-----------+   +-----------+
```

---

## 📝 Technologies Used

- AWS CDK (Python)
- Amazon EC2 (Amazon Linux 2)
- Amazon RDS (Aurora MySQL)
- Amazon VPC, ALB, IAM, SSM, Secrets Manager
- Apache HTTP Server
- PHP 8.1 and required Moodle extensions

---

## 📦 How to Deploy

### 🔧 1. Prerequisites

- AWS CLI configured
- CDK installed: `npm install -g aws-cdk`
- Python virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install CDK dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 🚀 2. Bootstrap & Deploy

```bash
cdk bootstrap
cdk deploy
```

This will:
- Provision the full AWS infrastructure
- Configure Apache, PHP, and Moodle via user data
- Deploy Moodle and database backend
- Output your ALB URL and RDS endpoint

---

## 🌐 Web Installer Instructions

1. Visit the ALB DNS (output by CDK)
2. Choose Language
3. Confirm web and moodledata directories
4. Select **MySQLi**
5. Enter DB details:
   - **Host**: `<Aurora endpoint>`
   - **User**: `moodleadmin`
   - **Password**: (get from Secrets Manager)
   - **DB Name**: `moodle` (you must create manually)

6. If needed, connect to EC2 (via SSM) and run:
```bash
mysql -h <endpoint> -u moodleadmin -p
CREATE DATABASE moodle DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🔐 Optional Enhancements

- Enable HTTPS via ACM + ALB listener
- Mount Amazon EFS for `/var/www/moodledata`
- Add backup and monitoring with AWS Backup + CloudWatch
- Create CI/CD pipeline using CodePipeline + CodeBuild

---

## 🧑‍💻 Author

**Christopher Corbin**  
Cloud | DevOps | Cybersecurity | AWS CDK  
Barbados 🇧🇧
