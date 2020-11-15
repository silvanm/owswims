<template>
  <div class="ribbon ribbon-top-right">
    <span><slot></slot></span>
  </div>
</template>

<script>
export default {
  name: 'Ribbon',
}
</script>

<style scoped>
/* common */
.ribbon {
  width: 150px;
  height: 150px;
  overflow: hidden;
  position: absolute;
}
.ribbon::before,
.ribbon::after {
  position: absolute;
  z-index: -1;
  content: '';
  display: block;
  border: 5px solid #2980b9;
}
.ribbon span {
  position: absolute;
  display: block;
  width: 225px;
  padding: 3px 0;
  background-color: #36abff;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
  color: #fff;
  font-size: 14px;
  text-align: center;
}

/* top right*/
.ribbon-top-right {
  top: 0px;
  right: 0px;
}
.ribbon-top-right::before,
.ribbon-top-right::after {
  border-top-color: transparent;
  border-right-color: transparent;
}
.ribbon-top-right::before {
  top: 0;
  left: 0;
}
.ribbon-top-right::after {
  bottom: 0;
  right: 0;
}
.ribbon-top-right span {
  left: 0px;
  top: 0px;
  transform: rotate(45deg);
}
</style>
