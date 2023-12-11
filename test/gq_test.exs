defmodule GqTest do
  use ExUnit.Case
  doctest Gq

  test "greets the world" do
    assert Gq.hello() == :world
  end
end
