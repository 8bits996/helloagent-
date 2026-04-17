# Project Context Document

> **Template for CLAUDE.md - Customizable for any project**

---

## 🎯 Project Overview

**Project Name**: [Your Project Name]

**Description**: [Brief description of what the project does and its main purpose]

**Tech Stack**:
- Frontend: [e.g., Next.js 14, React, TypeScript, Tailwind CSS]
- Backend: [e.g., Node.js, Express, Python FastAPI]
- Database: [e.g., PostgreSQL, MongoDB, Redis]
- ORM: [e.g., Prisma, Drizzle, SQLAlchemy]
- Testing: [e.g., Vitest, Jest, Playwright]
- Deployment: [e.g., Vercel, AWS, Docker]

**Project Status**: [Development/Production/Beta]

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │ ←──→ │   Backend   │ ←──→ │  Database   │
│  (Next.js)  │      │  (Express)  │      │ (PostgreSQL)│
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                    ┌──────▼──────┐
                    │    Cache    │
                    │   (Redis)   │
                    └─────────────┘
```

### Directory Structure

```
project-root/
├── app/              # Next.js App Router pages
├── components/       # Reusable React components
├── lib/              # Utility functions and configurations
├── types/            # TypeScript type definitions
├── prisma/           # Database schema and migrations
├── api/              # API routes (if using Express)
├── tests/            # Test files
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── e2e/          # End-to-end tests
└── docs/             # Documentation
```

### Key Modules

| Module | Description | Files |
|--------|-------------|-------|
| Authentication | User auth and session management | `lib/auth.ts`, `app/api/auth/*` |
| Database | Database operations and ORM | `lib/db.ts`, `prisma/schema.prisma` |
| API | RESTful API endpoints | `api/routes/*` |
| UI Components | Reusable UI components | `components/ui/*` |

---

## 💻 Development Standards

### Code Style

```typescript
// ✅ Good: Use TypeScript strict mode with explicit types
interface User {
  id: string;
  email: string;
  name: string;
}

async function getUser(id: string): Promise<User | null> {
  return await db.user.findUnique({ where: { id } });
}

// ❌ Bad: Avoid 'any' type
function processData(data: any) {  // DON'T DO THIS
  return data;
}

// ✅ Good: Use proper error handling
try {
  const result = await riskyOperation();
  return { success: true, data: result };
} catch (error) {
  console.error('Operation failed:', error);
  return { success: false, error: 'User-friendly error message' };
}
```

### Naming Conventions

- **Files**: Use kebab-case: `user-service.ts`, `api-client.ts`
- **Components**: Use PascalCase: `UserProfile.tsx`, `NavigationMenu.tsx`
- **Functions**: Use camelCase: `getUserById()`, `calculateTotal()`
- **Constants**: Use SCREAMING_SNAKE_CASE: `MAX_RETRY_COUNT`, `API_BASE_URL`
- **Types/Interfaces**: Use PascalCase with descriptive names: `UserProfile`, `ApiResponse`

### Git Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add user authentication
fix: resolve login timeout issue
docs: update API documentation
style: format code with Prettier
refactor: extract common validation logic
test: add unit tests for user service
chore: update dependencies
```

### Branch Strategy

- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: New features
- `fix/*`: Bug fixes
- `release/*`: Release preparation

---

## 🔒 Security Guidelines

### Authentication & Authorization

- Use [Clerk/Auth0/NextAuth] for authentication
- Implement role-based access control (RBAC)
- Never store passwords in plain text
- Use secure session management (HTTP-only cookies)

### Data Protection

```typescript
// ✅ Good: Validate and sanitize user input
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  name: z.string().min(2).max(50),
});

function validateUser(input: unknown) {
  return UserSchema.safeParse(input);
}

// ✅ Good: Use parameterized queries (Prisma does this by default)
const user = await db.user.findFirst({
  where: { email: userInput }  // Safe from SQL injection
});

// ❌ Bad: Never log sensitive data
console.log('User password:', password);  // DON'T DO THIS
```

### Environment Variables

Never commit `.env` files. Use `.env.example` as a template:

```bash
# .env.example
DATABASE_URL=postgresql://user:password@localhost:5432/db
NEXT_PUBLIC_API_URL=https://api.example.com
SECRET_KEY=your-secret-key-here
```

### API Security

- Implement rate limiting (e.g., 100 requests/minute per user)
- Use CORS with specific allowed origins
- Validate all API inputs with Zod
- Return consistent error responses

---

## 🧪 Testing Requirements

### Test Coverage

- **Minimum Coverage**: 80%
- **Critical Paths**: 100% (auth, payments, data operations)
- **Run Tests**: Before every commit (via pre-commit hook)

### Testing Stack

```typescript
// Unit Test Example (Vitest)
import { describe, it, expect } from 'vitest';
import { calculateTotal } from './cart';

describe('calculateTotal', () => {
  it('should calculate total correctly', () => {
    const items = [
      { price: 10, quantity: 2 },
      { price: 5, quantity: 3 },
    ];
    expect(calculateTotal(items)).toBe(35);
  });
});

// E2E Test Example (Playwright)
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

### Test Commands

```bash
# Run all tests
npm test

# Run unit tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run tests in watch mode
npm run test:watch
```

---

## 🚀 Performance Guidelines

### Frontend Performance

- Use Next.js `Image` component for all images
- Implement lazy loading for heavy components
- Use React.memo() for expensive components
- Optimize bundle size with dynamic imports

```typescript
// ✅ Good: Dynamic import for code splitting
const HeavyComponent = dynamic(
  () => import('./HeavyComponent'),
  { loading: () => <LoadingSpinner /> }
);

// ✅ Good: Memoize expensive computations
const ExpensiveList = memo(({ items }) => {
  return items.map(item => <Item key={item.id} {...item} />);
});
```

### Backend Performance

- Use Redis for caching frequently accessed data
- Implement database connection pooling
- Use pagination for large datasets
- Add database indexes for frequently queried fields

```typescript
// ✅ Good: Implement caching
async function getUser(id: string) {
  // Check cache first
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);
  
  // Fetch from database
  const user = await db.user.findUnique({ where: { id } });
  
  // Cache for 1 hour
  await redis.setex(`user:${id}`, 3600, JSON.stringify(user));
  
  return user;
}
```

### Database Optimization

- Use Prisma's `include` and `select` wisely to avoid over-fetching
- Create indexes for commonly queried fields
- Use transactions for multi-step operations
- Implement soft deletes with `deletedAt` timestamp

---

## 🔧 Common Tasks

### Adding a New API Endpoint

1. Create the route handler in `app/api/` or `api/routes/`
2. Define input validation with Zod
3. Implement business logic
4. Add error handling
5. Write integration tests
6. Update API documentation

### Adding a New Component

1. Create component in `components/` directory
2. Use TypeScript with proper type definitions
3. Follow component naming convention (PascalCase)
4. Add Storybook story (if applicable)
5. Write unit tests
6. Export from `components/index.ts`

### Database Migration

```bash
# Create a new migration
npx prisma migrate dev --name add_user_table

# Apply migrations to production
npx prisma migrate deploy

# Reset database (development only)
npx prisma migrate reset
```

---

## 🐛 Debugging & Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Database connection timeout | Too many connections | Use connection pooling |
| Type errors in tests | Missing type definitions | Add types to `types/` directory |
| Slow API response | N+1 query problem | Use Prisma `include` properly |
| Memory leak | Uncleaned subscriptions | Use useEffect cleanup |

### Debug Tools

- **Database**: Prisma Studio (`npx prisma studio`)
- **API**: Postman/Insomnia for manual testing
- **Frontend**: React DevTools, Next.js debug mode
- **Performance**: Lighthouse, Chrome DevTools Performance tab

---

## 📚 Documentation Links

- **Next.js**: https://nextjs.org/docs
- **Prisma**: https://www.prisma.io/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Vitest**: https://vitest.dev/guide/
- **Playwright**: https://playwright.dev/docs/intro

---

## 🤝 Contributing

### Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes with proper tests
3. Ensure all tests pass: `npm test`
4. Update documentation if needed
5. Submit PR with clear description
6. Address review feedback
7. Squash and merge when approved

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Test coverage maintained or improved
- [ ] No TypeScript errors
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] Commit messages follow convention

---

## 📞 Support

- **Tech Lead**: [Name] (@username)
- **Slack Channel**: #project-name
- **Issue Tracker**: GitHub Issues
- **Documentation**: [Link to docs]

---

**Last Updated**: 2025-03-19  
**Maintained By**: [Your Team Name]
