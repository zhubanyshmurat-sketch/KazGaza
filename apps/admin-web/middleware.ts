import { NextRequest, NextResponse } from "next/server";

// Edge-level guard: a missing access_token cookie means the user is
// definitely not authenticated, so bounce them to /login before any
// page code runs. Cookie presence alone is not proof of validity — the
// backend still verifies the JWT signature/expiry on every API call,
// and the client-side AuthProvider redirects on a 401 from /auth/me too.
export function middleware(request: NextRequest) {
  const hasSession = request.cookies.has("access_token");
  const { pathname } = request.nextUrl;

  if (!hasSession && pathname !== "/login") {
    const loginUrl = new URL("/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  if (hasSession && pathname === "/login") {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
