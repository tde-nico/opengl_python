import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '40,40'

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import numpy as np
import pyrr

WIDTH = 1200
HEIGHT = 720


vertex_src = '''
# version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;

uniform mat4 model;
uniform mat4 projection;

out vec3 v_color;
out vec2 v_texture;

void main()
{
	gl_Position = projection * model * vec4(a_position, 1.0);
	v_texture = a_texture;
}
'''

fragment_src = '''
# version 330 core

in vec2 v_texture;

out vec4 out_color;

uniform sampler2D s_texture;

void main()
{
	out_color = texture(s_texture, v_texture); // * vec4(v_color, 1.0);
}
'''


vertices = [
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

indices = [
	0, 1, 2, 2, 3, 0,
	4, 5, 6, 6, 7, 4,
	8, 9, 10, 10, 11, 8,
	12, 13, 14, 14, 15, 12,
	16, 17, 18, 18, 19, 16,
	20, 21, 22, 22, 23, 20
]

vertices = np.array(vertices, dtype=np.float32)
indices = np.array(indices, dtype=np.uint32)

pygame.init()
pygame.display.set_mode((WIDTH,HEIGHT), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
	compileShader(fragment_src, GL_FRAGMENT_SHADER))

VBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

EBO = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)


glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize*5, ctypes.c_void_p(12))


texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


image = pygame.image.load('textures/crate.jpg')
image = pygame.transform.flip(image, False, True)
image_width, image_height = image.get_rect().size
img_data = pygame.image.tostring(image, 'RGBA')
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width,
	image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)



glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

#projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH/HEIGHT, 0.1, 100)
projection = pyrr.matrix44.create_orthogonal_projection_matrix(0, WIDTH, 0, HEIGHT, -1000, 1000)
translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([400,200,-3]))
scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([200, 200, 200]))

model_loc = glGetUniformLocation(shader, 'model')
proj_loc = glGetUniformLocation(shader, 'projection')

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

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

	rot_x = pyrr.Matrix44.from_x_rotation(0.5 * ct)
	rot_y = pyrr.Matrix44.from_y_rotation(0.8 * ct)

	rotation = pyrr.matrix44.multiply(rot_x, rot_y)
	model = pyrr.matrix44.multiply(scale, rotation)
	model = pyrr.matrix44.multiply(model, translation)
	
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

	glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

	pygame.display.flip()

pygame.quit()
