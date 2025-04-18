import { toggleSection } from "./login.js";

document.addEventListener("DOMContentLoaded", () => {
  const navButtons = document.querySelectorAll("nav button");

  navButtons.forEach(button => {
    button.addEventListener("click", () => {
      const targetId = button.getAttribute("data-target");
      if (targetId) {
        toggleSection(targetId);
      }
    });
  });
});
