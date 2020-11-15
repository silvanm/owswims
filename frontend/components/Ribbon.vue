<template>
  <div class="ribbon ribbon-bottom-right">
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
.ribbon-bottom-right {
  bottom: 0;
  right: 0;
}
.ribbon-bottom-right::before,
.ribbon-bottom-right::after {
  border-bottom-color: transparent;
  border-right-color: transparent;
}
.ribbon-bottom-right::before {
  bottom: 0;
  left: 0;
}
.ribbon-bottom-right::after {
  top: 0;
  right: 0;
}
.ribbon-bottom-right span {
  left: 13px;
  bottom: 7px;
  transform: rotate(-45deg);
}
</style>
