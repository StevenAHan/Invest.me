window.scrollBy(0, 100);

gsap.from(".listitem", {
    opacity: 0,
    duration: 0.5,
    x: 50,
    stagger: 1.2,
  });

gsap.fromTo('h1.banner-title', {y: 200,  opacity: 0}, {y: 0, delay: 5, duration: 3, opacity: 1})


