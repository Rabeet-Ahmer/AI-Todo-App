import { NextRequest, NextResponse } from 'next/server';
import { getSessionCookie } from 'better-auth/cookies';

export function middleware(request: NextRequest) {
  const sessionCookie = getSessionCookie(request);
  const { pathname } = request.nextUrl;

  // Redirect authenticated users from login/signup pages
  if (sessionCookie && ['/login', '/register'].includes(pathname)) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Protect dashboard routes
  if (!sessionCookie && pathname.startsWith('/dashboard')) {
    // Store the attempted URL for redirect after login
    const redirectUrl = encodeURIComponent(request.url);
    return NextResponse.redirect(new URL(`/login?redirect=${redirectUrl}`, request.url));
  }

  // Check for expired session by attempting to validate the token
  // If the session cookie exists but is invalid/expired, redirect to login
  if (sessionCookie && pathname.startsWith('/dashboard')) {
    // We'll validate the session by checking if the API call succeeds
    // This is handled in the requireAuth function in auth.actions.ts
    // The middleware will allow the request to proceed and let the server components handle validation
  }

  return NextResponse.next();
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