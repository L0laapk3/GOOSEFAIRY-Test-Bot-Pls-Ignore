class PythonExample(BaseAgent):



    def initialize_agent(self):

        # This runs once before the bot starts up

        self.controller_state = SimpleControllerState()



    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:

        ball_location = Vec3(packet.game_ball.physics.location)



        my_car = packet.game_cars[self.index]

        car_location = Vec3(my_car.physics.location)



        car_to_ball = ball_location - car_location



        # Find the direction of our car using the Orientation class

        car_orientation = Orientation(my_car.physics.rotation)

        car_direction = car_orientation.forward
        
        controller = SimpleControllerState()



        steer_correction_radians = find_correction(car_direction, car_to_ball)



        if steer_correction_radians > 3:
            
            if car_direction - car_to_ball > 2: 

            turn = -1.0
            
            throttle = 0.4

            action_display = "turn left"
            
            else:
            
            turn = 1.0
            
            throttle = 0.4

            action_display = "turn right"

        else:

            throttle = 1.0
            
            

        self.controller_state.steer = turn
        
        self.controller_state.throttle = throttle



        draw_debug(self.renderer, my_car, packet.game_ball, action_display)



        return self.controller_state
