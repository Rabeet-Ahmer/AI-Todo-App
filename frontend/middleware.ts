import { NextRequest, NextResponse } from 'next/server';

/**
 * Minimal middleware for route protection.
 * Using Node.js runtime for better compatibility with cookie operations.
 */
export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Check for Better Auth session cookie
  const cookies = request.cookies;
  let hasSessionCookie = false;
  
  try {
    for (const cookie of cookies.getAll()) {
      if (cookie.name.startsWith('better-auth.')) {
        hasSessionCookie = true;
        break;
      }
    }
  } catch (e) {
    // If cookie reading fails, assume no session
    hasSessionCookie = false;
  }

  // Redirect authenticated users from login/signup pages
  if (hasSessionCookie && (pathname === '/login' || pathname === '/register')) {
    try {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    } catch (e) {
      return NextResponse.next();
    }
  }

  // Protect dashboard routes
  if (!hasSessionCookie && pathname.startsWith('/dashboard')) {
    try {
      const redirectUrl = encodeURIComponent(request.url);
      return NextResponse.redirect(new URL(`/login?redirect=${redirectUrl}`, request.url));
    } catch (e) {
      return NextResponse.next();
    }
  }

  return NextResponse.next();
}

// Simplified matcher - only match specific routes that need protection
// Using Node.js runtime instead of Edge to avoid compatibility issues
export const config = {
  runtime: 'nodejs', // Use Node.js runtime instead of Edge for better compatibility
  matcher: [
    '/dashboard/:path*',
    '/login',
    '/register'
  ],
};
