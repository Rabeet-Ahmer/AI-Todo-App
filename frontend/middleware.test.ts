/**
 * ABSOLUTE MINIMAL TEST VERSION
 * 
 * If this file works when renamed to middleware.ts, then the issue
 * is in the logic. If this also fails, the issue is environmental.
 * 
 * To test: Rename this to middleware.ts temporarily
 */
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Absolute minimal - just pass through
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
