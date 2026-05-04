// ============================================
// Tracking Module
// ============================================

import { apiRequest } from "./api.js";

/**
 * Track parcel by tracking ID (public endpoint - no auth needed)
 * Expects: tracking_id (e.g., "SS2024001234")
 * Returns: { tracking_id, status, parcel_id, events: [...] }
 */
export async function trackParcel(trackingId) {
  try {
    const response = await apiRequest(
      `/api/tracking/track/${trackingId}/`,
      "GET"
    );
    return response;
  } catch (error) {
    throw error;
  }
}