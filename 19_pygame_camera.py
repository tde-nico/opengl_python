import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '40,40'

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
import pygame
from texture import load_texture_pygame
from ObjLoader import ObjLoader
from camera import Camera

WIDTH = 1200
HEIGHT = 720

lastX = 0
lastY = 0

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


cube_indices, cube_buffer = ObjLoader.load_model("meshes/cube.obj")
monkey_indices, monkey_buffer = ObjLoader.load_model("meshes/monkey.obj")
floor_indices, floor_buffer = ObjLoader.load_model("meshes/floor.obj")

shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

VAO = glGenVertexArrays(3)
VBO = glGenBuffers(3)

# cube
glBindVertexArray(VAO[0])

glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
glBufferData(GL_ARRAY_BUFFER, cube_buffer.nbytes, cube_buffer, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, cube_buffer.itemsize * 8, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, cube_buffer.itemsize * 8, ctypes.c_void_p(12))

glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, cube_buffer.itemsize * 8, ctypes.c_void_p(20))
glEnableVertexAttribArray(2)

# monkey
glBindVertexArray(VAO[1])

glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
glBufferData(GL_ARRAY_BUFFER, monkey_buffer.nbytes, monkey_buffer, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(12))

glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, monkey_buffer.itemsize * 8, ctypes.c_void_p(20))
glEnableVertexAttribArray(2)

# floor
glBindVertexArray(VAO[2])

glBindBuffer(GL_ARRAY_BUFFER, VBO[2])
glBufferData(GL_ARRAY_BUFFER, floor_buffer.nbytes, floor_buffer, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, floor_buffer.itemsize * 8, ctypes.c_void_p(0))

glEnableVertexAttribArray(1)
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, floor_buffer.itemsize * 8, ctypes.c_void_p(12))

glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, floor_buffer.itemsize * 8, ctypes.c_void_p(20))
glEnableVertexAttribArray(2)


textures = glGenTextures(3)
load_texture_pygame("meshes/cube.jpg", textures[0])
load_texture_pygame("meshes/monkey.jpg", textures[1])
load_texture_pygame("meshes/floor.jpg", textures[2])

glUseProgram(shader)
glClearColor(0, 0.1, 0.1, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

projection = pyrr.matrix44.create_perspective_projection_matrix(45, WIDTH / HEIGHT, 0.1, 100)
cube_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([6, 4, 0]))
monkey_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([-4, 4, -4]))
floor_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))


model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


running = True

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
xpos, ypos = 0,0

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

	# movement
	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_w]:
		cam.process_keyboard('FORWARD', 0.05)
	if keys_pressed[pygame.K_s]:
		cam.process_keyboard('BACKWARD', 0.05)
	if keys_pressed[pygame.K_a]:
		cam.process_keyboard('LEFT', 0.05)
	if keys_pressed[pygame.K_d]:
		cam.process_keyboard('RIGHT', 0.05)

	# Camera movement
	if mouse_move != (0,0):
		xpos += mouse_move[0]
		ypos += mouse_move[1]

		xoffset = xpos - lastX
		yoffset = lastY - ypos

		lastX = xpos
		lastY = ypos

		cam.process_mouse_movement(xoffset, yoffset)

	# Other

	ct = pygame.time.get_ticks() / 1000

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	view = cam.get_view_matrix()
	glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

	rot_y = pyrr.Matrix44.from_y_rotation(0.8 * ct)
	model = pyrr.matrix44.multiply(rot_y, cube_pos)

	# draw the cube
	glBindVertexArray(VAO[0])
	glBindTexture(GL_TEXTURE_2D, textures[0])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
	glDrawArrays(GL_TRIANGLES, 0, len(monkey_indices))

	# draw the monkey
	glBindVertexArray(VAO[1])
	glBindTexture(GL_TEXTURE_2D, textures[1])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, monkey_pos)
	glDrawArrays(GL_TRIANGLES, 0, len(monkey_indices))

	# draw the floor
	glBindVertexArray(VAO[2])
	glBindTexture(GL_TEXTURE_2D, textures[2])
	glUniformMatrix4fv(model_loc, 1, GL_FALSE, floor_pos)
	glDrawArrays(GL_TRIANGLES, 0, len(floor_indices))

	pygame.display.flip()

pygame.quit()
