from .svgfiguremod import SVGFigureModule


class SVGFigureFACS(SVGFigureModule):
    def __init__(self, svg):
        super().__init__(svg)
        
        
    def add_facs_scale(self,
                       x=0,
                       y=0,
                       w=100,
                       padding=20,
                       ticks=[('-10^2', 0.01), 
                              ('0', 0.17), 
                              ('10^2', 0.32),
                              ('10^3', 0.54),
                              ('10^4', 0.74),
                              ('10^5', 0.92)],
                       axis='x'):
        #self.svg.set_font_size(libsvg.FIGURE_FONT_SIZE)
        
        offset = 0.75 * self.svg.get_font_h()
        
        if axis == 'x':
            y += self.svg.get_font_h() + padding
        
            for tick in ticks:
                x1 = x + tick[1] * w
                
                label = tick[0]
                
                if '^' not in label:
                    label = '{}^'.format(label)
                    
                number, power = label.split('^')
                
                swn = self.svg.get_string_width(number)
                swp = self.svg.get_string_width(power)
                
                sw = swn + swp
                
                x2 = x1 - sw / 2
                
                self.svg.add_text_bb(number, x=x2, y=y)
                
                if power != '':
                    x2 += swn
                    self.svg.add_text_bb(power, x=x2, y=y-offset)
        else:
            x -= self.svg.get_string_width('8') #padding
        
            for tick in ticks:
                y1 = y - tick[1] * w
                
                label = tick[0]
                
                if '^' not in label:
                    label = '{}^'.format(label)
                    
                number, power = label.split('^')
                
                swn = self.svg.get_string_width(number)
                swp = self.svg.get_string_width(power)
                
                sw = swn + swp
                
                x1 = x - sw / 2
                
                self.svg.add_text_bb(number, x=x, y=y1, align='r')
                
                if power != '':
                    self.svg.add_text_bb(power, x=x, y=y1-offset)
        
        #self.svg.set_font_size(libsvg.DEFAULT_FONT_SIZE)
