import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

vertex_src = '''
# version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_color;

out vec3 v_color;

void main()
{
	gl_Position = vec4(a_position, 1.0);
	v_color = a_color;
}
'''

fragment_src = '''
# version 330 core

in vec3 v_color;

out vec4 out_color;

void main()
{
	out_color = vec4(v_color, 1.0);
}
'''

def window_resize(window, width, height):
	glViewport(0, 0, width, height)


if not glfw.init():
	raise Exception("glfw can not be initialized")

window = glfw.create_window(1280, 720, 'My OpenGL Window', None, None)

if not window:
	glfw.terminate()
	raise Exception("glfw window can not be created")

glfw.set_window_pos(window, 40, 40)

glfw.set_window_size_callback(window, window_resize)

glfw.make_context_current(window)

vertices = [
	-0.5, -0.5, 0.0,	1.0, 0.0, 0.0,
	0.5, -0.5, 0.0,		0.0, 1.0, 0.0,
	-0.5, 0.5, 0.0,		0.0, 0.0, 1.0,
	0.5, 0.5, 0.0,		1.0, 1.0, 1.0,
	0.0, 0.75, 0.0,		1.0, 1.0, 0.0
]

indices = [
	0, 1, 2,
	1, 2, 3,
	2, 3, 4
]

vertices = np.array(vertices, dtype=np.float32)
indices = np.array(indices, dtype=np.uint32)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
	compileShader(fragment_src, GL_FRAGMENT_SHADER))

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)


glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)

while not glfw.window_should_close(window):
	glfw.poll_events()

	glClear(GL_COLOR_BUFFER_BIT)

	glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

	glfw.swap_buffers(window)

glfw.terminate()
