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
  const response = await fetch("http://localhost:3000/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: `{
        efficiency(userId: ${userId}) {
          light
          rem
          deep
          efficiency
          smoke
          exercise
        }
      }`
    })
  });
  const json = await response.json();
  return json?.data?.efficiency;
}

export async function fetchUserLog(userId) {
  const response = await fetch("http://localhost:3000/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: `{
        log(userId: ${userId}) {
          ts
          temperature
          humidity
          heartrate
        }
      }`
    })
  });
  const json = await response.json();
  return json?.data?.log;
}