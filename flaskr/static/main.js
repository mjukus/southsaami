const navToggle = document.querySelector(".mobile-nav-toggle");
const iconClose = document.querySelector(".mobile-nav-toggle .icon-close")
const iconHamburger = document.querySelector(".mobile-nav-toggle .icon-hamburger")
const primaryNav = document.querySelector(".primary-navigation");
const article = document.querySelector("article")
const articleTitle = document.querySelector(".secondary-heading")

navToggle.addEventListener('click', () => {
  primaryNav.hasAttribute("data-visible")
  ? navToggle.setAttribute('aria-expanded', false)
  : navToggle.setAttribute('aria-expanded', true);
  primaryNav.toggleAttribute("data-visible");
  iconClose.toggleAttribute("data-visible");
  iconHamburger.toggleAttribute("data-visible");

})