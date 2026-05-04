// ============================================
// Parcel Management Module
// ============================================

import { apiRequest } from "./api.js";

/**
 * Create a new parcel
 * Expects: {
 *   sender_name, receiver_name,
 *   source_pincode, destination_pincode,
 *   weight, dimensions (optional),
 *   description (optional)
 * }
 * Returns: { parcel_id, tracking_id, status }
 */
export async function createParcel(data) {
  try {
    const response = await apiRequest("/api/parcel/create/", "POST", data);
    return response;
  } catch (error) {
    throw error;
  }
}

/**
 * Confirm a parcel (payment/order confirmation)
 * Expects: parcel_id
 * Returns: { parcel_id, status, tracking_id }
 */
export async function confirmParcel(parcelId) {
  try {
    const response = await apiRequest(
      `/api/parcel/confirm/${parcelId}/`,
      "POST"
    );
    return response;
  } catch (error) {
    throw error;
  }
}

/**
 * Get all parcels for current user
 * Returns: [ { parcel_id, tracking_id, status, ... }, ... ]
 */
export async function getMyParcels() {
  try {
    const response = await apiRequest("/api/parcel/my-parcels/", "GET");
    // Handle both array and paginated response
    if (Array.isArray(response)) {
      return response;
    }
    if (response.results) {
      return response.results;
    }
    return [];
  } catch (error) {
    throw error;
  }
}

/**
 * Get details for a specific parcel
 * Expects: parcel_id
 * Returns: { parcel_id, tracking_id, status, sender_name, receiver_name, ... }
 */
export async function getParcelDetail(parcelId) {
  try {
    const response = await apiRequest(
      `/api/parcel/my-parcels/${parcelId}/`,
      "GET"
    );
    return response;
  } catch (error) {
    throw error;
  }
}

export async function getParcelCheckout(parcelId) {
  try {
    const response = await apiRequest(
      `/api/parcel/checkout/${parcelId}/`,
      "GET"
    );
    return response;
  } catch (error) {
    throw error;
  }
}

/**
 * Cancel a parcel
 * Expects: parcel_id
 * Returns: { parcel_id, status }
 */
export async function cancelParcel(parcelId) {
  try {
    const response = await apiRequest(
      `/api/parcel/cancel/${parcelId}/`,
      "POST"
    );
    return response;
  } catch (error) {
    throw error;
  }
}