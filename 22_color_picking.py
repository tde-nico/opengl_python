import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '40,40'

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import pyrr
import numpy as np

from texture import load_texture_pygame


WIDTH, HEIGHT = 1280, 720



mouse_x, mouse_y = 0, 0
red_rot = False
green_rot = False
blue_rot = False
picker = False


def pick():
	global red_rot, green_rot, blue_rot, picker

	data = glReadPixels(mouse_x, mouse_y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)

	if data[0] == 255:
		red_rot = not red_rot
	elif data[1] == 255:
		green_rot = not green_rot
	elif data[2] == 255:
		blue_rot = not blue_rot
	picker = False


vertex_src = """
# version 330
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 v_texture;

void main()
{
	gl_Position = projection * view * model * vec4(a_position, 1.0);
	v_texture = a_texture;
}
"""

fragment_src = """
# version 330

in vec2 v_texture;

out vec4 out_color;

uniform sampler2D s_texture;
uniform ivec3 icolor;
uniform int switcher;

void main()
{
	if(switcher == 0){
		out_color = texture(s_texture, v_texture);
	}else{
		out_color = vec4(icolor.r/255.0, icolor.g/255.0, icolor.b/255.0, 1.0);
	}
}
"""

pygame.init()
pygame.display.set_mode((WIDTH,HEIGHT), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)


cube_buffer = [
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

cube_buffer = np.array(cube_buffer, dtype=np.float32)

cube_indices = [
	0, 1, 2, 2, 3, 0,
	4, 5, 6, 6, 7, 4,
	8, 9, 10, 10, 11, 8,
	12, 13, 14, 14, 15, 12,
	16, 17, 18, 18, 19, 16,
	20, 21, 22, 22, 23, 20
]

cube_indices = np.array(cube_indices, dtype=np.uint32)


shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))


VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)
EBO = glGenBuffers(1)


glBindVertexArray(VAO)

glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, cube_buffer.nbytes, cube_buffer, GL_STATIC_DRAW)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, cube_indices.nbytes, cube_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_buffer.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_buffer.itemsize * 5, ctypes.c_void_p(12))

textures = glGenTextures(3)
crate = load_texture_pygame("textures/crate.jpg", textures[0])
metal = load_texture_pygame("textures/metal.jpg", textures[1])
brick = load_texture_pygame("textures/brick.jpg", textures[2])


pick_texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, pick_texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_FLOAT, None)

FBO = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, FBO)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, pick_texture, 0)
glBindFramebuffer(GL_FRAMEBUFFER, 0)
glBindTexture(GL_TEXTURE_2D, 0)

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH / HEIGHT, 0.1, 100)
view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -4.0]))

cube_positions = [(-2.0, 0.0, 0.0), (0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]
pick_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")
icolor_loc = glGetUniformLocation(shader, "icolor")
switcher_loc = glGetUniformLocation(shader, "switcher")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)


running = True

mouse_picker = False

while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.VIDEORESIZE:
			glViewport(0, 0, event.w, event.h)
			projection = pyrr.matrix44.create_perspective_projection_matrix(45, event.w/event.h, 0.1, 100)
			glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1 and not mouse_picker: # 1 -> left click
				picker = True
				mouse_picker = True
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1: # 1 -> left click
				mouse_picker = False

	mouse_x, mouse_y = pygame.mouse.get_pos()

	ct = pygame.time.get_ticks() / 1000

	glClearColor(0, 0.1, 0.1, 1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	rot_y = pyrr.Matrix44.from_y_rotation(ct * 2)

	glUniform1i(switcher_loc, 0)
	for i in range(len(cube_positions)):
		model = pyrr.matrix44.create_from_translation(cube_positions[i])
		if i == 0:
			glBindTexture(GL_TEXTURE_2D, crate)
			if red_rot:
				glUniformMatrix4fv(model_loc, 1, GL_FALSE, rot_y @ model)
			else:
				glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
		elif i == 1:
			glBindTexture(GL_TEXTURE_2D, metal)
			if green_rot:
				glUniformMatrix4fv(model_loc, 1, GL_FALSE, rot_y @ model)
			else:
				glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
		else:
			glBindTexture(GL_TEXTURE_2D, brick)
			if blue_rot:
				glUniformMatrix4fv(model_loc, 1, GL_FALSE, rot_y @ model)
			else:
				glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

		glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)


	glUniform1i(switcher_loc, 1)
	glBindFramebuffer(GL_FRAMEBUFFER, FBO)
	glClearColor(0.0, 0.0, 0.0, 1.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	for i in range(len(cube_positions)):
		pick_model = pyrr.matrix44.create_from_translation(cube_positions[i])
		glUniform3iv(icolor_loc, 1, pick_colors[i])
		glUniformMatrix4fv(model_loc, 1, GL_FALSE, pick_model)
		glDrawElements(GL_TRIANGLES, len(cube_indices), GL_UNSIGNED_INT, None)

	if picker:
		pick()

	glBindFramebuffer(GL_FRAMEBUFFER, 0)

	pygame.display.flip()


pygame.quit()
