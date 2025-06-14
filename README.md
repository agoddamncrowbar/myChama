# ChamaLink - Digital Chama Management Platform

## Project Description

**Market Need**: Traditional chamas (investment groups) in Kenya rely on manual record-keeping, cash transactions, and in-person meetings, leading to inefficiencies, disputes over contributions, and limited financial transparency. With Kenya's mobile money adoption at over 80%, there's a significant opportunity to digitize chama operations.

**Project Value**: ChamaLink transforms how Kenyan investment groups operate by providing a comprehensive digital platform that automates contribution tracking, integrates M-Pesa payments, manages loans, and offers real-time financial insights. This reduces administrative burden, increases transparency, and enables chamas to scale their operations effectively.

**Key Benefits**:
- Automated M-Pesa integration for seamless contributions
- Real-time financial tracking and reporting
- Digital loan management with automated calculations
- Goal setting and progress visualization
- Reduced disputes through transparent record-keeping
- Mobile-first design for accessibility

## Target Users

### Primary Users
- **Chama Administrators**: Group leaders who manage day-to-day operations, track contributions, and oversee financial decisions
- **Chama Members**: Individual participants who make contributions, apply for loans, and track their financial progress
- **Chama Treasurers**: Financial officers responsible for managing group funds, loan approvals, and financial reporting

### User Demographics
- **Geographic**: Kenya (with potential expansion to East Africa)
- **Age**: 25-55 years old
- **Income**: Middle to lower-middle class
- **Tech Proficiency**: Basic to intermediate smartphone users
- **Group Size**: Chamas with 5-50 members

### Use Cases
- **Small Business Chamas**: Groups saving for business investments
- **Housing Chamas**: Members pooling funds for property purchases
- **Education Chamas**: Parents saving for children's school fees
- **Emergency Fund Chamas**: Groups creating safety nets for members

## How to Run the Project

### Prerequisites
- Node.js 18+ and npm/yarn
- PostgreSQL database
- M-Pesa developer account (Safaricom Daraja API)

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/allansh/chamalink.git
   cd chamalink
   ```

2. **Install Dependencies**
   ```bash
   # Backend setup
   cd backend
   npm install
   
   # Frontend setup
   cd ../frontend
   npm install
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment templates
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Update with your credentials:
   # - Database connection string
   # - M-Pesa API credentials
   # - JWT secrets
   ```

4. **Database Setup**
   ```bash
   cd backend
   npx prisma generate
   npx prisma db push
   npx prisma db seed
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend (Port 3001)
   cd backend
   npm run dev
   
   # Terminal 2 - Frontend (Port 3000)
   cd frontend
   npm start
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001
   - API Documentation: http://localhost:3001/api-docs

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL="postgresql://user:password@localhost:5432/chamalink"
JWT_SECRET="your-jwt-secret"
MPESA_CONSUMER_KEY="your-mpesa-key"
MPESA_CONSUMER_SECRET="your-mpesa-secret"
MPESA_SHORTCODE="174379"
MPESA_PASSKEY="your-passkey"
```

**Frontend (.env)**
```env
REACT_APP_API_URL="http://localhost:3001/api"
REACT_APP_MPESA_CONSUMER_KEY="your-mpesa-key"
```

## Team Members

| Name | Role | GitHub Handle | Responsibilities |
|------|------|---------------|------------------|
| **Allan Sharad** | Lead Developer & Co-Founder | [@allansh](https://github.com/allansh) | Backend development, M-Pesa integration, database design |
| **Iqbal Sharif** | Frontend Developer & Co-Founder | [@iqbalsharif](https://github.com/iqbalsharif) | UI/UX design, React development, mobile responsiveness |

### Contact Information
- **Project Lead**: Allan Sharad (allan@chamalink.co.ke)
- **Technical Lead**: Iqbal Sharif (iqbal@chamalink.co.ke)

## Project Timeline

### Phase 1: MVP Development (Q1 2025) - COMPLETED
**Duration**: January - March 2025
- [x] Project setup and architecture
- [x] User authentication system
- [x] Basic chama creation and management
- [x] Member management functionality
- [x] M-Pesa STK Push integration
- [x] Contribution tracking

### Phase 2: Core Features (Q2 2025) - IN PROGRESS
**Duration**: April - June 2025
- [ ] Loan management system
- [ ] Payment reminders and notifications
- [ ] Financial reporting dashboard
- [ ] Goal setting and tracking
- [ ] Mobile app development (React Native)
- [ ] Beta testing with 10 chamas

### Phase 3: Advanced Features (Q3 2025) - PLANNED
**Duration**: July - September 2025
- [ ] Advanced analytics and insights
- [ ] Multi-chama management
- [ ] Investment tracking
- [ ] Integration with banks and SACCOs
- [ ] Automated loan calculations
- [ ] Public launch and marketing

### Phase 4: Scale & Expansion (Q4 2025) - PLANNED
**Duration**: October - December 2025
- [ ] AI-powered financial insights
- [ ] Multi-language support (Swahili)
- [ ] Expansion to Uganda and Tanzania
- [ ] Partnership with financial institutions
- [ ] Advanced security features
- [ ] 1000+ active chamas target

### Key Milestones
- **MVP Launch**: March 31, 2025
- **Beta Release**: June 30, 2025
- **Public Launch**: September 30, 2025
- **Regional Expansion**: December 31, 2025

## Link to Project Board

**Project Management**: [GitHub Project Board](https://github.com/users/allansh/projects/1)

### Board Structure
- **Backlog**: Features and improvements waiting to be prioritized
- **Todo**: Items ready for development in current sprint
- **In Progress**: Actively being worked on
- **Review**: Completed work awaiting code review
- **Done**: Completed and deployed features

### Sprint Schedule
- **Sprint Duration**: 2 weeks
- **Sprint Planning**: Every other Monday
- **Sprint Review**: Every other Friday
- **Daily Standups**: Monday, Wednesday, Friday (virtual)

---



**Built for the Kenyan chama community**
