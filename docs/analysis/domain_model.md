# Domain Model – MyChama

The domain model represents the main entities and relationships within the MyChama platform, which is designed to support group savings (chamas), contributions, loans, meetings, and communication among members.

---

## 1. Entities and Descriptions

### 🧍 Member
Represents an individual user within the platform.
- **Attributes**:
  - member_id
  - full_name
  - phone_number
  - email
  - role (e.g., Chairperson, Treasurer, Member)
  - joined_date
  - chama_id (foreign key)

---

### 👥 Chama (Savings Group)
The organizational unit under which members operate.
- **Attributes**:
  - chama_id
  - name
  - description
  - created_by (Admin or Founder)
  - creation_date

---

### 💰 Contribution
Tracks regular member contributions to the chama fund.
- **Attributes**:
  - contribution_id
  - member_id
  - chama_id
  - amount
  - contribution_date
  - payment_method (e.g., M-Pesa)

---

### 🏦 Loan
Represents loans requested and approved within the group.
- **Attributes**:
  - loan_id
  - member_id
  - amount
  - status (e.g., pending, approved, rejected)
  - interest_rate
  - repayment_schedule
  - approved_by (Chairperson)
  - issued_date

---

### 🧾 Repayment
Tracks repayments made by members on their loans.
- **Attributes**:
  - repayment_id
  - loan_id
  - member_id
  - amount
  - repayment_date

---

### 📆 Meeting
Tracks scheduled meetings and agendas for chama groups.
- **Attributes**:
  - meeting_id
  - chama_id
  - topic
  - meeting_date
  - location
  - notes

---

### 📢 Announcement
Messages sent by admins or leaders to members.
- **Attributes**:
  - announcement_id
  - chama_id
  - title
  - message
  - sent_by
  - timestamp

---

### 📊 Poll
Used for decision-making within the group.
- **Attributes**:
  - poll_id
  - chama_id
  - question
  - options
  - created_by
  - expiry_date

---

## 2. Relationships (Simplified)

- A **Chama** has many **Members**
- A **Member** can make many **Contributions**
- A **Member** can request many **Loans**
- A **Loan** has many **Repayments**
- A **Chama** schedules many **Meetings**
- A **Chama** can have multiple **Announcements** and **Polls**
- A **Poll** collects votes from **Members**

---

## 3. Notes

- All monetary transactions are linked with member IDs for transparency.
- Roles (Chairperson, Treasurer, Member) determine access and actions within the app.
- Every action or data entry is timestamped for audit purposes.

