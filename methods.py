import pygame

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width() /
                      2, win.get_height()/2 - render.get_height()/2))

def draw_skid_mark(win, pos, angle, alpha, size=(4, 10), color=(25, 25, 25)):
    if alpha <= 0:
        return
    mark = pygame.Surface(size, pygame.SRCALPHA)
    mark.fill((*color, min(alpha, 255)))
    rotated = pygame.transform.rotate(mark, angle)
    rect = rotated.get_rect(center=(round(pos.x), round(pos.y)))
    win.blit(rotated, rect)