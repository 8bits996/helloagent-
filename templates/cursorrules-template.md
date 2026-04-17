# .cursorrules Template

> **AI Behavior Rules for Cursor IDE**  
> **Copy this file to your project root and customize**

---

## 🎯 Project Context

### Tech Stack
- Framework: [Next.js / React / Vue / etc.]
- Language: [TypeScript / JavaScript]
- Styling: [Tailwind CSS / CSS Modules / styled-components]
- Database: [PostgreSQL / MongoDB / etc.]
- ORM: [Prisma / Drizzle / etc.]
- Testing: [Vitest / Jest / Playwright]

### Project Type
- [ ] Frontend Application
- [ ] Backend API
- [ ] Full-Stack Application
- [ ] CLI Tool
- [ ] Library/Package

---

## 📝 Code Style Rules

### General Principles

```typescript
// ✅ DO: Use TypeScript strict mode
// ✅ DO: Prefer const over let
// ✅ DO: Use meaningful variable names
// ✅ DO: Keep functions small and focused (max 50 lines)
// ✅ DO: Use early returns to reduce nesting

// ❌ DON'T: Use 'any' type
// ❌ DON'T: Create deeply nested code (max 3 levels)
// ❌ DON'T: Write long functions (> 50 lines)
// ❌ DON'T: Use magic numbers without constants
// ❌ DON'T: Leave console.log in production code
```

### TypeScript Guidelines

```typescript
// ✅ Good: Explicit return types
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// ✅ Good: Use interfaces for object shapes
interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

// ✅ Good: Use type guards
function isUser(obj: unknown): obj is User {
  return typeof obj === 'object' && obj !== null && 'id' in obj && 'email' in obj;
}

// ✅ Good: Use const assertions for readonly arrays
const ROUTES = ['/home', '/about', '/contact'] as const;

// ❌ Bad: Using 'any'
function process(data: any) {  // DON'T DO THIS
  return data;
}
```

### React Best Practices

```typescript
// ✅ Good: Functional components with TypeScript
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({ 
  label, 
  onClick, 
  variant = 'primary' 
}) => {
  return (
    <button 
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
};

// ✅ Good: Custom hooks for reusable logic
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// ✅ Good: Memoize expensive components
const ExpensiveList = memo(({ items }: { items: Item[] }) => {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
});

// ❌ Bad: Prop drilling (use context or state management instead)
// ❌ Bad: Storing derived state (compute on the fly)
```

### Next.js Specific

```typescript
// ✅ Good: Use Server Components by default
// app/users/page.tsx
async function UsersPage() {
  const users = await db.user.findMany();  // Direct DB query
  
  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}

// ✅ Good: Use Client Components only when needed
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}

// ✅ Good: Use Next.js Image component
import Image from 'next/image';

<Image 
  src="/profile.jpg" 
  alt="Profile" 
  width={200} 
  height={200}
  priority  // For above-the-fold images
/>

// ❌ Bad: Using <img> tag directly (loses optimization)
// ❌ Bad: Fetching data in Client Components (use Server Components)
```

---

## 🔒 Security Rules

### Input Validation

```typescript
// ✅ Good: Always validate user input with Zod
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain uppercase letter')
    .regex(/[0-9]/, 'Password must contain number'),
  age: z.number().min(18, 'Must be 18 or older').optional(),
});

function validateUser(input: unknown) {
  const result = UserSchema.safeParse(input);
  if (!result.success) {
    throw new Error(result.error.errors[0].message);
  }
  return result.data;
}

// ❌ Bad: Trusting user input blindly
function processUserInput(input: any) {  // DON'T DO THIS
  return input;
}
```

### SQL Injection Prevention

```typescript
// ✅ Good: Use parameterized queries (Prisma does this by default)
const user = await db.user.findFirst({
  where: { 
    email: userInput,  // Safe
    AND: { active: true }
  }
});

// ✅ Good: Use Prisma's raw query with parameters
const result = await db.$queryRaw`
  SELECT * FROM users 
  WHERE email = ${userInput}  // Safe: parameterized
`;

// ❌ Bad: String concatenation in SQL
const query = `SELECT * FROM users WHERE email = '${userInput}'`;  // NEVER DO THIS
await db.$queryRawUnsafe(query);  // DANGEROUS
```

### Authentication & Authorization

```typescript
// ✅ Good: Check authentication in Server Components
import { auth } from '@/lib/auth';

async function ProtectedPage() {
  const session = await auth();
  
  if (!session) {
    redirect('/login');
  }
  
  // Only authenticated users reach here
  return <Dashboard />;
}

// ✅ Good: Role-based access control
async function AdminPage() {
  const session = await auth();
  
  if (session?.user.role !== 'admin') {
    return <AccessDenied />;
  }
  
  return <AdminDashboard />;
}

// ❌ Bad: Relying only on client-side checks
'use client';

function AdminPage() {
  // DON'T DO THIS - easily bypassed
  if (localStorage.getItem('role') !== 'admin') {
    return <AccessDenied />;
  }
  return <AdminDashboard />;
}
```

---

## 🎨 Styling Rules

### Tailwind CSS

```typescript
// ✅ Good: Use Tailwind utility classes
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <span className="text-lg font-semibold text-gray-900">Title</span>
  <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Action
  </button>
</div>

// ✅ Good: Extract repeated patterns to components
const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={`p-6 bg-white rounded-lg shadow-md ${className}`}>
    {children}
  </div>
);

// ✅ Good: Use Tailwind's responsive prefixes
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => <Item key={item.id} {...item} />)}
</div>

// ❌ Bad: Inline styles (unless dynamic)
<div style={{ color: 'red' }}>  {/* Avoid if possible */}
  Text
</div>
```

---

## 🧪 Testing Rules

### Unit Tests

```typescript
// ✅ Good: Test behavior, not implementation
describe('UserService', () => {
  it('should create user with valid data', async () => {
    const data = { email: 'test@example.com', name: 'Test' };
    const user = await UserService.create(data);
    
    expect(user).toBeDefined();
    expect(user.email).toBe(data.email);
    expect(user.id).toBeDefined();
  });
  
  it('should reject invalid email', async () => {
    const data = { email: 'invalid-email', name: 'Test' };
    
    await expect(UserService.create(data)).rejects.toThrow('Invalid email');
  });
});

// ✅ Good: Use descriptive test names
it('should return null when user not found', async () => {
  const user = await UserService.getById('non-existent-id');
  expect(user).toBeNull();
});

// ❌ Bad: Testing implementation details
it('should call database with correct query', async () => {
  // Testing internal implementation, not behavior
});
```

### E2E Tests

```typescript
// ✅ Good: Test user flows
import { test, expect } from '@playwright/test';

test('user can complete checkout flow', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="cart-icon"]');
  await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();
  
  await page.click('[data-testid="checkout-button"]');
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('[data-testid="place-order"]');
  
  await expect(page).toHaveURL('/order-confirmation');
});

// ✅ Good: Use data-testid for reliable selectors
<button data-testid="submit-button">Submit</button>
```

---

## ⚡ Performance Rules

### Data Fetching

```typescript
// ✅ Good: Fetch in parallel when possible
const [users, products, orders] = await Promise.all([
  db.user.findMany(),
  db.product.findMany(),
  db.order.findMany(),
]);

// ✅ Good: Use React Query for client-side caching
import { useQuery } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
  
  if (isLoading) return <Loading />;
  return <Profile user={user} />;
}

// ❌ Bad: Waterfall requests
const users = await db.user.findMany();
const products = await db.product.findMany();  // Waits for users to finish
const orders = await db.order.findMany();      // Waits for products to finish
```

### Database Optimization

```typescript
// ✅ Good: Use Prisma select to fetch only needed fields
const users = await db.user.findMany({
  select: {
    id: true,
    email: true,
    name: true,
    // Exclude sensitive fields like password
  },
});

// ✅ Good: Use indexes on frequently queried fields
model User {
  id        String   @id @default(cuid())
  email     String   @unique  // Creates index
  name      String
  createdAt DateTime @default(now())
  
  @@index([email, createdAt])  // Composite index
}

// ✅ Good: Implement pagination
const posts = await db.post.findMany({
  skip: (page - 1) * pageSize,
  take: pageSize,
  orderBy: { createdAt: 'desc' },
});

// ❌ Bad: Fetching all data without pagination
const posts = await db.post.findMany();  // Could fetch millions of records
```

---

## 🚨 Error Handling

### API Error Responses

```typescript
// ✅ Good: Consistent error responses
try {
  const result = await processData(input);
  return NextResponse.json({ 
    success: true, 
    data: result 
  });
} catch (error) {
  console.error('Process failed:', error);
  
  if (error instanceof ValidationError) {
    return NextResponse.json(
      { 
        success: false, 
        error: {
          code: 'VALIDATION_ERROR',
          message: error.message,
        }
      },
      { status: 400 }
    );
  }
  
  return NextResponse.json(
    { 
      success: false, 
      error: {
        code: 'INTERNAL_ERROR',
        message: 'An unexpected error occurred',
      }
    },
    { status: 500 }
  );
}

// ❌ Bad: Exposing internal errors
return NextResponse.json(
  { error: error.stack },  // NEVER expose stack traces
  { status: 500 }
);
```

---

## 📦 File Organization

### Component Structure

```
components/
├── ui/                 # Basic UI components (Button, Input, etc.)
│   ├── Button.tsx
│   ├── Input.tsx
│   └── index.ts
├── features/           # Feature-specific components
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   └── dashboard/
│       └── StatsCard.tsx
└── layouts/            # Layout components
    ├── Header.tsx
    └── Footer.tsx
```

### API Route Structure

```
app/api/
├── users/
│   ├── route.ts        # GET /api/users, POST /api/users
│   └── [id]/
│       └── route.ts    # GET /api/users/:id, PUT /api/users/:id
├── auth/
│   ├── login/
│   │   └── route.ts    # POST /api/auth/login
│   └── register/
│       └── route.ts    # POST /api/auth/register
└── health/
    └── route.ts        # GET /api/health
```

---

## 🔄 Git Workflow

### Branch Naming

```
feature/add-user-authentication
fix/login-timeout-issue
refactor/database-layer
docs/api-documentation
test/user-service-tests
```

### Commit Messages

```
feat(auth): add JWT token refresh mechanism
fix(api): resolve database connection timeout
docs(readme): update installation instructions
refactor(user): extract validation logic to separate file
test(auth): add integration tests for login flow
```

---

## 📋 Pre-commit Rules

Before every commit, ensure:

- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] All tests pass
- [ ] Code formatted with Prettier
- [ ] No sensitive data in code
- [ ] No console.log statements (except in utilities)
- [ ] Proper error handling implemented
- [ ] Documentation updated (if needed)

---

## 🚫 Anti-Patterns to Avoid

1. **Prop Drilling**: Use Context or state management instead
2. **God Components**: Break large components into smaller ones
3. **Premature Optimization**: Profile before optimizing
4. **Copy-Paste Code**: Extract to reusable functions
5. **Hardcoded Values**: Use environment variables or constants
6. **Deep Nesting**: Use early returns and guard clauses
7. **Large useEffect**: Split into multiple effects or custom hooks
8. **Stale State**: Use functional updates when state depends on previous state

---

**Remember**: These rules are guidelines, not laws. Use judgment and discuss with team if a rule doesn't make sense for your specific case.
