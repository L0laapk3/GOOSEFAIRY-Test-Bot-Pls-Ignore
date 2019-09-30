def test(self):
        car = CarState(boost_amount=100, physics=Physics(velocity=vector3(0,0,0),angular_velocity=vector3(0,0,0),location=vector3(3000,3000,20),rotation=Rotator(0,1.5,0)))
        ball = BallState(physics=Physics(location=vector3(0,-side(self.team)*3000,94),angular_velocity=vector3(0,0,0), velocity=vector3(0,0,3000)))
        game = GameState(ball=ball, cars = {self.index: car})
        self.set_game_state(game)
