import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '40,40'

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import numpy as np
import pyrr

from texture import load_texture_pygame
from camera import Camera


WIDTH = 1200
HEIGHT = 720


lastX = 0
lastY = 0

cam = Camera()


vertex_src = '''
# version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_offset;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 move;

out vec2 v_texture;

void main()
{
	vec3 final_pos = a_position + a_offset;
	gl_Position = projection * view * move * model * vec4(final_pos, 1.0f);
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
	out_color = texture(s_texture, v_texture);
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


VAO = glGenVertexArrays(1)
VBO = glGenBuffers(1)
EBO = glGenBuffers(1)


glBindVertexArray(VAO)

glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize * 5, ctypes.c_void_p(12))

textures = glGenTextures(1)
cube_texture = load_texture_pygame("textures/crate.jpg", textures)


instance_array = []
offset = 1

for z in range(0, 100, 2):
	for y in range(0, 100, 2):
		for x in range(0, 100, 2):
			translation = pyrr.Vector3([0.0, 0.0, 0.0])
			translation.x = x + offset
			translation.y = y + offset
			translation.z = z + offset
			instance_array.append(translation)

len_of_instance_array = len(instance_array)
instance_array = np.array(instance_array, np.float32).flatten()

instanceVBO = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, instanceVBO)
glBufferData(GL_ARRAY_BUFFER, instance_array.nbytes, instance_array, GL_STATIC_DRAW)

glEnableVertexAttribArray(2)
glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
glVertexAttribDivisor(2, 1)

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH / HEIGHT, 0.1, 100)
cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-50.0, -50.0, -195.0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")
move_loc = glGetUniformLocation(shader, "move")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(model_loc, 1, GL_FALSE, cube_pos)


running = True


pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
xpos, ypos = 0,0
speed = 0.3


while running:
	mouse_move = (0,0)
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
		elif event.type == pygame.MOUSEMOTION:
			if event.rel[0] - lastX or event.rel[1] - lastY:
				mouse_move = event.rel
				lastX = xpos
				lastY = ypos

	# Movement
	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_w]:
		cam.process_keyboard('FORWARD', speed)
	if keys_pressed[pygame.K_s]:
		cam.process_keyboard('BACKWARD', speed)
	if keys_pressed[pygame.K_a]:
		cam.process_keyboard('LEFT', speed)
	if keys_pressed[pygame.K_d]:
		cam.process_keyboard('RIGHT', speed)


	# Camera
	if mouse_move != (0,0):
		xpos += mouse_move[0]
		ypos += mouse_move[1]
		xoffset = xpos - lastX
		yoffset = lastY - ypos
		lastX = xpos
		lastY = ypos
		cam.process_mouse_movement(xoffset, yoffset)


	# Time
	ct = pygame.time.get_ticks() / 1000

	# Render
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	move = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0])) # ct*8
	glUniformMatrix4fv(move_loc, 1, GL_FALSE, move)

	view = cam.get_view_matrix()
	glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

	glDrawElementsInstanced(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None, len_of_instance_array)




	pygame.display.flip()

pygame.quit()
