import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '40,40'

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
import pyrr
import numpy as np

from texture import load_texture_pygame
from ObjLoader import ObjLoader
from camera import Camera


WIDTH, HEIGHT = 1280, 720


lastX, lastY = WIDTH / 2, HEIGHT / 2
cam = Camera()


vertex_src = """
# version 330

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_normal;

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

void main()
{
	out_color = texture(s_texture, v_texture);
}
"""

pygame.init()
pygame.display.set_mode((WIDTH,HEIGHT), pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)


chibi_indices, chibi_buffer = ObjLoader.load_model("meshes/chibi.obj")


plane_buffer = [
	0.0, 0.0, 0.0, 0.0, 0.0,
	10.0, 0.0, 0.0, 1.0, 0.0,
	10.0, 10.0, 0.0, 1.0, 1.0,
	0.0, 10.0, 0.0, 0.0, 1.0
]

plane_buffer = np.array(plane_buffer, dtype=np.float32)

plane_indices = [0, 1, 2, 2, 3, 0]
plane_indices = np.array(plane_indices, dtype=np.uint32)

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))


VAO = glGenVertexArrays(2)
VBO = glGenBuffers(2)
EBO = glGenBuffers(1)


glBindVertexArray(VAO[0])

glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
glBufferData(GL_ARRAY_BUFFER, chibi_buffer.nbytes, chibi_buffer, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, chibi_buffer.itemsize * 8, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, chibi_buffer.itemsize * 8, ctypes.c_void_p(12))

glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, chibi_buffer.itemsize * 8, ctypes.c_void_p(20))
glEnableVertexAttribArray(2)



glBindVertexArray(VAO[1])

glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
glBufferData(GL_ARRAY_BUFFER, plane_buffer.nbytes, plane_buffer, GL_STATIC_DRAW)

glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, plane_indices.nbytes, plane_indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, plane_buffer.itemsize * 5, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, plane_buffer.itemsize * 5, ctypes.c_void_p(12))

textures = glGenTextures(2)
load_texture_pygame("meshes/chibi.png", textures[0])


glBindTexture(GL_TEXTURE_2D, textures[1])

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1280, 720, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
glBindTexture(GL_TEXTURE_2D, 0)

depth_buff = glGenRenderbuffers(1)
glBindRenderbuffer(GL_RENDERBUFFER, depth_buff)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, 1280, 720)

FBO = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, FBO)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, textures[1], 0)
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buff)
glBindFramebuffer(GL_FRAMEBUFFER, 0)

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)
chibi_pos_main = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, -5]))
plane_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-20, -3, -10]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)



running = True


pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
xpos, ypos = 0,0
speed = 0.08


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


	ct = pygame.time.get_ticks() / 1000


	glClearColor(0, 0.1, 0.1, 1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	view = cam.get_view_matrix()
	glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

	rot_y = pyrr.Matrix44.from_y_rotation(0.8 * ct)
	model = pyrr.matrix44.multiply(rot_y, chibi_pos_main)

	glBindVertexArray(VAO[0])
	glBindTexture(GL_TEXTURE_2D, textures[0])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
	glDrawArrays(GL_TRIANGLES, 0, len(chibi_indices))

	glBindFramebuffer(GL_FRAMEBUFFER, FBO)
	glClearColor(0.0, 0.0, 0.0, 1.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glDrawArrays(GL_TRIANGLES, 0, len(chibi_indices))
	glBindVertexArray(0)
	glBindFramebuffer(GL_FRAMEBUFFER, 0)

	glBindVertexArray(VAO[1])
	glBindTexture(GL_TEXTURE_2D, textures[1])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, plane_pos)
	glDrawElements(GL_TRIANGLES, len(plane_indices), GL_UNSIGNED_INT, None)

	pygame.display.flip()


pygame.quit()
