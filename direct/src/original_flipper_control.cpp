// Generated verbatim from vendored TFlipper.cpp. See vendor/LICENSE.
#include "flipper.h"

int TFlipper::GetFlipperStepAngle(float dt, float* dst) const
{
	if (!MessageField)
		return 0;

	auto deltaAngle = FlipperEdge->flipper_angle_delta(dt);
	auto step = std::fabs(std::ceil(FlipperEdge->DistanceDiv * deltaAngle * FlipperEdge->InvT1Radius));
	if (step > 3.0f)
		step = 3.0f;
	if (step >= 2.0f)
	{
		*dst = deltaAngle / step;
		return static_cast<int>(step);
	}

	*dst = deltaAngle;
	return 1;
}

void TFlipper::FlipperCollision(float deltaAngle)
{
	if (!MessageField)
		return;

	ray_type ray{}, rayDst{};
	ray.MinDistance = 0.002f;
	bool collisionFlag = false;
	for (auto ball : pb::MainTable->BallList)
	{
		if ((FlipperEdge->CollisionGroup & ball->CollisionMask) != 0 &&
			FlipperEdge->YMax >= ball->Position.Y && FlipperEdge->YMin <= ball->Position.Y &&
			FlipperEdge->XMax >= ball->Position.X && FlipperEdge->XMin <= ball->Position.X)
		{
			if (FlipperEdge->ControlPointDirtyFlag)
				FlipperEdge->set_control_points(FlipperEdge->CurrentAngle);
			ray.CollisionMask = ball->CollisionMask;
			ray.Origin = ball->Position;

			float sin, cos;
			auto ballPosRot = ray.Origin;
			maths::SinCos(-deltaAngle, sin, cos);
			maths::RotatePt(ballPosRot, sin, cos, FlipperEdge->RotOrigin);
			ray.Direction.X = ballPosRot.X - ray.Origin.X;
			ray.Direction.Y = ballPosRot.Y - ray.Origin.Y;
			ray.MaxDistance = maths::normalize_2d(ray.Direction);
			auto distance = maths::distance_to_flipper(FlipperEdge, ray, rayDst);
			if (distance < 1e9f)
			{
				FlipperEdge->NextBallPosition = ball->Position;
				FlipperEdge->CollisionDirection = rayDst.Direction;
				FlipperEdge->EdgeCollision(ball, distance);
				collisionFlag = true;
			}
		}
	}

	if (collisionFlag)
	{
		auto angleAdvance = deltaAngle / (std::fabs(FlipperEdge->MoveSpeed) * 5.0f);
		FlipperEdge->CurrentAngle -= angleAdvance;
		FlipperEdge->AngleRemainder += std::fabs(angleAdvance);
	}
	else
	{
		FlipperEdge->CurrentAngle += deltaAngle;
		FlipperEdge->AngleRemainder -= std::fabs(deltaAngle);
	}

	if (FlipperEdge->AngleRemainder <= 0.0001f)
	{
		FlipperEdge->CurrentAngle = FlipperEdge->AngleDst;
		FlipperEdge->FlipperFlag = MessageCode::TFlipperNull;
		MessageField = 0;
	}
	FlipperEdge->ControlPointDirtyFlag = true;
}
