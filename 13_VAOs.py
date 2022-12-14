import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '40,40'

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import numpy as np
import pyrr

from texture import load_texture_pygame


WIDTH = 1200
HEIGHT = 720


vertex_src = '''
# version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec3 v_color;
out vec2 v_texture;

void main()
{
	gl_Position = projection * view * model * vec4(a_position, 1.0);
	v_texture = a_texture;
	v_color = a_color;
}
'''

fragment_src = '''
# version 330 core

in vec2 v_texture;
in vec3 v_color;

out vec4 out_color;
uniform int switcher;

uniform sampler2D s_texture;

void main()
{
	if (switcher == 0){
		out_color = texture(s_texture, v_texture);
	}
	else if (switcher == 1){
		out_color = vec4(v_color, 1.0);
	}
}
'''


cube_vertices = [
	-0.5, -0.5, 0.5,	0.0, 0.0,
	0.5, -0.5, 0.5,		1.0, 0.0,
	0.5, 0.5, 0.5,		1.0, 1.0,
	-0.5, 0.5, 0.5,		0.0, 1.0,

	-0.5, -0.5, -0.5,	0.0, 0.0,
	0.5, -0.5, -0.5,	1.0, 0.0,
	0.5, 0.5, -0.5,		1.0, 1.0,
	-0.5, 0.5, -0.5,	0.0, 1.0,

	0.5, -0.5, -0.5,	0.0, 0.0,
	0.5, 0.5, -0.5,		1.0, 0.0,
	0.5, 0.5, 0.5,		1.0, 1.0,
	0.5, -0.5, 0.5,		0.0, 1.0,

	-0.5, 0.5, -0.5,	0.0, 0.0,
	-0.5, -0.5, -0.5,	1.0, 0.0,
	-0.5, -0.5, 0.5,	1.0, 1.0,
	-0.5, 0.5, 0.5,		0.0, 1.0,

	-0.5, -0.5, -0.5,	0.0, 0.0,
	0.5, -0.5, -0.5,	1.0, 0.0,
	0.5, -0.5, 0.5,		1.0, 1.0,
	-0.5, -0.5, 0.5,	0.0, 1.0,

	0.5, 0.5, -0.5,		0.0, 0.0,
	-0.5, 0.5, -0.5,	1.0, 0.0,
	-0.5, 0.5, 0.5,		1.0, 1.0,
	0.5, 0.5, 0.5,		0.0, 1.0
]

cube_indices = [
	0, 1, 2, 2, 3, 0,
	4, 5, 6, 6, 7, 4,
	8, 9, 10, 10, 11, 8,
	12, 13, 14, 14, 15, 12,
	16, 17, 18, 18, 19, 16,
	20, 21, 22, 22, 23, 20
]

cube_vertices = np.array(cube_vertices, dtype=np.float32)
cube_indices = np.array(cube_indices, dtype=np.uint32)

quad_vertices = [
	-0.5, -0.5, 0,	0.0, 0.0,
	0.5, -0.5, 0,	1.0, 0.0,
	0.5, 0.5, 0,	1.0, 1.0,
	-0.5, 0.5, 0,	0.0, 1.0
]

quad_indices = [0, 1, 2, 2, 3, 0]

quad_vertices = np.array(quad_vertices, dtype=np.float32)
quad_indices = np.array(quad_indices, dtype=np.uint32)

triangle_vertices = [
	-0.5, -0.5, 0,	1, 0, 0,
	0.5, -0.5, 0,	0, 1, 0,
	0.0, 0.5, 0,	0, 0, 1
]

triangle_vertices = np.array(triangle_vertices, dtype=np.float32)


pygame.init()
pygame.display.set_mode((WIDTH,HEIGHT), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
	compileShader(fragment_src, GL_FRAGMENT_SHADER))

# Cube
cube_VAO = glGenVertexArrays(1)
glBindVertexArray(cube_VAO)

cube_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, cube_VBO)
glBufferData(GL_ARRAY_BUFFER, cube_vertices.nbytes, cube_vertices, GL_STATIC_DRAW)

cube_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cube_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 5, ctypes.c_void_p(12))


# Quad
quad_VAO = glGenVertexArrays(1)
glBindVertexArray(quad_VAO)

quad_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, quad_VBO)
glBufferData(GL_ARRAY_BUFFER, quad_vertices.nbytes, quad_vertices, GL_STATIC_DRAW)

quad_EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, quad_EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, quad_indices.nbytes, quad_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_vertices.itemsize * 5, ctypes.c_void_p(12))


# Triangle
triangle_VAO = glGenVertexArrays(1)
glBindVertexArray(triangle_VAO)

triangle_VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, triangle_VBO)
glBufferData(GL_ARRAY_BUFFER, triangle_vertices.nbytes, triangle_vertices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, triangle_vertices.itemsize * 6, ctypes.c_void_p(0))

glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, triangle_vertices.itemsize * 6, ctypes.c_void_p(12))



texture = glGenTextures(2)

cube_texture = load_texture_pygame('textures/crate.jpg', texture[0])
quad_texture = load_texture_pygame('textures/cat.png', texture[1])


glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH/HEIGHT, 0.1, 100)
cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([1,0,0]))
quad_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-1,0,0]))
triangle_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0,1,-1]))



view = pyrr.matrix44.create_look_at(pyrr.Vector3([0,0,3]),
	pyrr.Vector3([0,0,0]), pyrr.Vector3([0,1,0]))


model_loc = glGetUniformLocation(shader, 'model')
proj_loc = glGetUniformLocation(shader, 'projection')
view_loc = glGetUniformLocation(shader, 'view')
switcher_loc = glGetUniformLocation(shader, 'switcher')

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

running = True

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			glViewport(0, 0, event.w, event.h)
			projection = pyrr.matrix44.create_perspective_projection_matrix(45, event.w/event.h, 0.1, 100)
			glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)



	ct = pygame.time.get_ticks() / 1000

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glUniform1i(switcher_loc, 0)

	rot_x = pyrr.Matrix44.from_x_rotation(0.5 * ct)
	rot_y = pyrr.Matrix44.from_y_rotation(0.8 * ct)

	rotation = pyrr.matrix44.multiply(rot_x, rot_y)

	model = pyrr.matrix44.multiply(rotation, cube_pos)

	glBindVertexArray(cube_VAO)
	glBindTexture(GL_TEXTURE_2D, texture[0])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
	glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

	model = pyrr.matrix44.multiply(rot_x, quad_pos)

	glBindVertexArray(quad_VAO)
	glBindTexture(GL_TEXTURE_2D, texture[1])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
	glDrawElements(GL_TRIANGLES, len(quad_indices), GL_UNSIGNED_INT, None)

	model = pyrr.matrix44.multiply(rot_y, triangle_pos)

	glBindVertexArray(triangle_VAO)
	glUniform1i(switcher_loc, 1)
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
	glDrawArrays(GL_TRIANGLES, 0, 3)


	pygame.display.flip()

pygame.quit()
