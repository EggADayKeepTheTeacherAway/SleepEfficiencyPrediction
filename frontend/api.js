export async function getSleepData() {
  const res = await fetch("/api/sleep"); // adjust this if your endpoint is different
  return await res.json();
}