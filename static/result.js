window.scrollBy(0, 135);

gsap.from(".listitem", {
    delay: 1,
    opacity: 0,
    duration: 0.5,
    x: 50,
    stagger: 1.2,
  });

gsap.fromTo('h1.banner-title', {y: 200,  opacity: 0}, {y: 0, delay: 6, duration: 3, opacity: 1})


