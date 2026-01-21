import { NextRequest, NextResponse } from 'next/server';

/**
 * Edge-compatible middleware for route protection.
 * Uses direct cookie access instead of better-auth/cookies helper
 * to ensure compatibility with Vercel Edge runtime.
 */
export function middleware(request: NextRequest) {
  try {
    const { pathname } = request.nextUrl;

    // Check for Better Auth session cookie (Edge-compatible)
    // Better Auth typically uses cookies starting with 'better-auth.'
    // Common names: 'better-auth.session_token' or 'better-auth.session'
    const allCookies = request.cookies.getAll();
    const hasSessionCookie = allCookies.some(
      (cookie) => cookie.name.startsWith('better-auth.')
    );

    // Redirect authenticated users from login/signup pages
    if (hasSessionCookie && ['/login', '/register'].includes(pathname)) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    // Protect dashboard routes
    if (!hasSessionCookie && pathname.startsWith('/dashboard')) {
      // Store the attempted URL for redirect after login
      const redirectUrl = encodeURIComponent(request.url);
      return NextResponse.redirect(new URL(`/login?redirect=${redirectUrl}`, request.url));
    }

    // Note: Session validation (expired/invalid tokens) is handled by
    // requireAuth() in server actions/components, not in middleware.
    // Middleware only checks for cookie presence for routing decisions.

    return NextResponse.next();
  } catch (error) {
    // Log error in production for debugging
    console.error('Middleware error:', error);
    // Allow request to proceed on error to avoid blocking all traffic
    // Server-side auth checks will handle validation
    return NextResponse.next();
  }
}

// Define which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
    // Also protect the dashboard routes
    '/dashboard/:path*',
    '/login',
    '/register'
  ],
};