export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || API_BASE_URL.replace(/^http/, "ws").replace(/\/api\/v1$/, "");
export const MEDIA_BASE_URL = process.env.NEXT_PUBLIC_MEDIA_URL || API_BASE_URL.replace(/\/api\/v1$/, "");
