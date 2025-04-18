document.addEventListener("DOMContentLoaded", () => {
  const navButtons = document.querySelectorAll("nav button");
  const sections = document.querySelectorAll(".content-section");

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");

      sections.forEach((section) => {
        section.classList.remove("active");
      });

      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.classList.add("active");
      }
    });
  });
});