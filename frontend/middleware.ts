import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Debug logging to see if middleware runs at all
  console.log("Middleware invoked for:", request.nextUrl.pathname);
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};