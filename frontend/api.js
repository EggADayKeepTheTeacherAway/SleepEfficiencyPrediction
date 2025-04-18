export async function getUserLog(user_id = 0) {
  try {
    const response = await fetch(`http://127.0.0.1:8080/sleep-api/log/${user_id}`);
    if (!response.ok) throw new Error("API fetch failed");
    return await response.json();
  } catch (err) {
    console.error("Error fetching user log:", err);
    return [];
  }
}

export async function fetchEfficiency(userId) {
  try {
    const response = await fetch(`http://127.0.0.1:8080/sleep-api/efficiency/${userId}`);
    if (!response.ok) throw new Error("API fetch failed");
    const data = await response.json();
    // Return the first efficiency record if it's an array
    return Array.isArray(data) ? data[0] : data;
  } catch (err) {
    console.error("Error fetching efficiency:", err);
    return null;
  }
}

export async function fetchUserLog(userId) {
  try {
    const response = await fetch(`http://127.0.0.1:8080/sleep-api/log/${userId}`);
    if (!response.ok) throw new Error("API fetch failed");
    return await response.json();
  } catch (err) {
    console.error("Error fetching user log:", err);
    return [];
  }
}

export async function fetchLatestData(userId) {
  try {
    const response = await fetch(`http://127.0.0.1:8080/sleep-api/latest/${userId}`);
    if (!response.ok) throw new Error("API fetch failed");
    return await response.json();
  } catch (err) {
    console.error("Error fetching latest data:", err);
    return null;
  }
}