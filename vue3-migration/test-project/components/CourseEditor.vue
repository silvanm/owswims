<template>
  <div class="course-editor">
    <div class="course-editor-content">
      <h3>Course Editor</h3>
      <p>This is a placeholder for the CourseEditor component.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseEditor',
  props: {
    map: {
      type: Object,
      required: true
    }
  }
}
</script>

<style>
.course-editor {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: white;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  z-index: 1000;
}

.course-editor-content {
  max-width: 300px;
}

.course-editor h3 {
  margin-top: 0;
  margin-bottom: 10px;
}
</style>
